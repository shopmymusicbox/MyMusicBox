# CalorieSnap

Take a photo of your meal. CalorieSnap estimates the calories and subtracts them from your daily goal as you log meals through the day.

## How it works

1. **Set a daily goal.** Enter a calorie number, or use the built-in calculator. It uses the Mifflin-St Jeor equation with your activity level and whether you want to lose, keep or gain weight.
2. **Snap a meal.** Take a photo, pick one from your library, or type a description such as "2 eggs in butter and a slice of toast". You can add a note to any photo, like "only ate half" or "cooked in olive oil".
3. **Review the estimate.** Each food is listed separately with grams, calories and protein, carbs and fat. You can:
   - change the grams of any item, and its calories and macros update to match
   - type in a calorie number yourself
   - untick items you didn't eat
   - tap ½, ¾, 1×, 1.5× or 2× for the whole plate
   - answer the app's one follow-up question (for example "Was this cooked in oil?") to get a better estimate
4. **Log it.** The ring shows how many calories you have left, turning amber when you're close to your goal and red when you're over. Macro bars, a 7-day chart and one-tap "Quick add" for meals you've logged before are also on the home screen.

## Why it's built this way

Reviews and tests of photo calorie apps (Cal AI, SnapCalorie, MyFitnessPal Meal Scan, Foodvisor and others) mostly report the same problems:

| Common complaint | What CalorieSnap does |
|---|---|
| Portion size is the biggest source of error | Each food gets its own gram estimate, judged against the plate, utensils and packaging in the photo, and you can change the grams |
| Hidden calories (oil, butter, dressing, sugar) are missed, so totals come out low | The AI adds likely hidden extras as separate items labeled **hidden extra**, so you can see them and untick the ones that don't apply |
| One number with no sense of how sure the app is | Shows a likely calorie range and a high, medium or low confidence label |
| You can't correct the AI | You can edit everything, add items by hand, and answer a follow-up question |
| Can't log by grams or describe a meal in words | Supports both |
| Paywalls, surprise trial charges | No account and no subscription. You pay only for your own AI usage, a fraction of a cent to a few cents per photo |
| Privacy | Your food log stays on your phone, in the browser's local storage. Photos go to the AI only to be analyzed, and only a small thumbnail is saved |

The estimates use Claude (`claude-opus-5-5`) with structured output, so results always come back in the same format. If the model declines a request for safety reasons, the API's automatic fallback is turned on and retries on another model.

## Run it

You need Node.js 18 or newer and an Anthropic API key (https://console.anthropic.com).

```bash
cd calorie-snap
npm install
ANTHROPIC_API_KEY=sk-ant-... npm start
```

Open http://localhost:3000.

**On your phone:** the camera needs HTTPS, except on `localhost`. The easiest way is to deploy the app to any Node host (Render, Railway, Fly.io and so on) with `ANTHROPIC_API_KEY` set as an environment variable. Then open the site on your phone and choose **Add to Home Screen**. It installs like an app.

Settings you can change with environment variables:

- `PORT`: default `3000`
- `CLAUDE_MODEL`: default `claude-opus-5-5`

## Limits

Calorie estimates from a photo are estimates. Even the best apps are typically off by 10–20%, and more for mixed or home-cooked dishes. For the most accurate numbers, include amounts in your note or edit the grams. Your log lives in one browser; use **Settings → Export my log (CSV)** to back it up.

## Files

- `server.js`: serves the app and calls Claude. Your API key stays on the server.
- `public/index.html`, `app.js`, `styles.css`: the app itself (plain JavaScript, no build step)
- `public/sw.js`, `manifest.webmanifest`, `icon.svg`: let you install it on your home screen and open it offline
