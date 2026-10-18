// CalorieSnap server: serves the web app and proxies meal analysis to Claude.
// The API key stays on the server; the browser never sees it.
import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { betaZodOutputFormat } from "@anthropic-ai/sdk/helpers/beta/zod";

const here = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(here, "public");
const PORT = Number(process.env.PORT) || 3000;
const MODEL = process.env.CLAUDE_MODEL || "claude-opus-5-5";
const MAX_BODY_BYTES = 12 * 1024 * 1024;

const client = new Anthropic();

const FoodItem = z.object({
  name: z.string().describe("Specific food name, e.g. 'grilled chicken thigh, skin on'"),
  portion: z.string().describe("Human-readable portion, e.g. '1 cup', '2 slices', '1 medium'"),
  grams: z.number().describe("Estimated edible weight in grams"),
  calories: z.number(),
  protein_g: z.number(),
  carbs_g: z.number(),
  fat_g: z.number(),
  hidden: z
    .boolean()
    .describe("True for likely-but-not-visible additions: cooking oil, butter, dressing, sugar in drinks, sauces"),
});

const MealAnalysis = z.object({
  is_food: z.boolean().describe("False if the image does not show food or drink"),
  meal_name: z.string().describe("Short title for the meal, e.g. 'Chicken burrito bowl'"),
  items: z.array(FoodItem),
  total_calories: z.number(),
  calorie_range_low: z.number().describe("Plausible lower bound for total calories"),
  calorie_range_high: z.number().describe("Plausible upper bound for total calories"),
  confidence: z.enum(["high", "medium", "low"]),
  clarifying_question: z
    .string()
    .describe("One short question whose answer would most improve accuracy, or empty string if none"),
  notes: z.string().describe("One or two sentences on assumptions made (portion, cooking method)"),
});

const SYSTEM_PROMPT = `You are a registered-dietitian-level nutrition estimator inside a calorie tracking app.
Estimate the nutrition of the meal the user shows or describes.

How to estimate well:
- Identify every distinct food and drink. Split mixed dishes into components (rice, protein, sauce, toppings) when that improves accuracy.
- Estimate portion size in grams using visual scale cues: plate (~26 cm dinner plate), bowl, utensils, hands, cans, packaging. State the portion in everyday units too.
- Use standard reference values (USDA FoodData Central style) for calories and macros per gram, then scale by your gram estimate.
- Photo-based apps most often UNDER-count. Explicitly add likely hidden calories as separate items marked hidden=true: cooking oil or butter on sauteed/fried/roasted food, dressings, sauces, sugar or milk in drinks, cheese under toppings. Only add what is genuinely likely for this dish.
- Restaurant and takeout portions are usually larger and oilier than home portions.
- If a packaged product or chain-restaurant item is recognizable, use its published nutrition.
- The user's note (if any) overrides what you see: trust stated amounts, ingredients, and cooking methods.
- total_calories must equal the sum of item calories (rounded). Give an honest range; widen it when portions are hard to judge.
- confidence: high = simple, clearly visible foods with good scale cues; low = mixed/hidden/occluded foods or poor photo.
- Ask a clarifying_question only when one answer would change the estimate meaningfully (e.g. "Was this cooked in oil or butter?", "Is that regular or diet soda?").
- If the image is not food, set is_food=false, return no items and zero totals.
Round calories to the nearest 5 and macros to whole grams.`;

async function analyzeMeal({ imageBase64, mediaType, note }) {
  const content = [];
  if (imageBase64) {
    content.push({
      type: "image",
      source: { type: "base64", media_type: mediaType, data: imageBase64 },
    });
  }
  content.push({
    type: "text",
    text: note?.trim() ? `User's note about this meal: ${note.trim()}` : "Estimate the nutrition of this meal.",
  });

  const response = await client.beta.messages.parse({
    model: MODEL,
    max_tokens: 16000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    output_config: { effort: "medium", format: betaZodOutputFormat(MealAnalysis) },
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content }],
  });

  if (response.stop_reason === "refusal") {
    throw new HttpError(422, "The model declined to analyze this image. Try another photo or describe the meal.");
  }
  if (!response.parsed_output) {
    throw new HttpError(502, "Could not read a nutrition estimate from the model. Please try again.");
  }
  return response.parsed_output;
}

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw new HttpError(413, "Image is too large.");
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new HttpError(400, "Invalid JSON body.");
  }
}

const ALLOWED_MEDIA = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);

async function handleAnalyze(req, res) {
  const body = await readJson(req);
  const { image, note } = body;
  let imageBase64 = null;
  let mediaType = null;
  if (image) {
    const match = /^data:(image\/[a-z]+);base64,(.+)$/.exec(image);
    if (!match || !ALLOWED_MEDIA.has(match[1])) throw new HttpError(400, "Unsupported image format.");
    [, mediaType, imageBase64] = match;
  }
  if (!imageBase64 && !note?.trim()) throw new HttpError(400, "Send a photo or describe your meal.");

  const result = await analyzeMeal({ imageBase64, mediaType, note: typeof note === "string" ? note.slice(0, 1000) : "" });
  sendJson(res, 200, result);
}

function sendJson(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(data));
}

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

async function serveStatic(req, res) {
  const urlPath = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const filePath = path.normalize(path.join(PUBLIC_DIR, urlPath === "/" ? "index.html" : urlPath));
  if (!filePath.startsWith(PUBLIC_DIR)) throw new HttpError(403, "Forbidden");
  try {
    const data = await fs.readFile(filePath);
    res.writeHead(200, { "Content-Type": MIME[path.extname(filePath)] || "application/octet-stream" });
    res.end(data);
  } catch {
    throw new HttpError(404, "Not found");
  }
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "POST" && req.url === "/api/analyze") return await handleAnalyze(req, res);
    if (req.method === "GET") return await serveStatic(req, res);
    throw new HttpError(405, "Method not allowed");
  } catch (err) {
    let status = err instanceof HttpError ? err.status : 500;
    let message = err instanceof HttpError ? err.message : "Something went wrong analyzing your meal.";
    if (err instanceof Anthropic.AuthenticationError || /authentication method/i.test(err?.message)) {
      message = "Server is missing a valid ANTHROPIC_API_KEY.";
    } else if (err instanceof Anthropic.RateLimitError) {
      status = 429;
      message = "Too many requests right now. Wait a moment and try again.";
    } else if (err instanceof Anthropic.APIConnectionError) {
      status = 503;
      message = "Could not reach the AI service. Check your connection.";
    } else if (err instanceof Anthropic.APIError) {
      status = 502;
      message = "The AI service returned an error. Please try again.";
    }
    if (!(err instanceof HttpError)) console.error(err);
    if (!res.headersSent) sendJson(res, status, { error: message });
  }
});

server.listen(PORT, () => {
  console.log(`CalorieSnap running at http://localhost:${PORT}`);
  if (!process.env.ANTHROPIC_API_KEY) console.warn("Warning: ANTHROPIC_API_KEY is not set; meal analysis will fail.");
});
