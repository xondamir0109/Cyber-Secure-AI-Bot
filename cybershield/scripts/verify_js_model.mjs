/**
 * KRITIK TEKSHIRUV: JavaScript versiyasi (predict.mjs + .mjs model fayllari)
 * sklearn modeli bilan AYNAN bir xil natija berishini tasdiqlaydi.
 *
 * Bu skript telegram-webhook.mjs FUNKSIYASI ISHLATADIGAN aynan shu .mjs
 * fayllarni import qiladi -- bu haqiqiy production kodini tekshiradi.
 */

import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";
import { predict } from "../netlify/functions/lightweight_model/predict.mjs";
import wordFeatures from "../netlify/functions/lightweight_model/word_features.mjs";
import charFeatures from "../netlify/functions/lightweight_model/char_features.mjs";
import modelConfig from "../netlify/functions/lightweight_model/config.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const referencePath = path.join(__dirname, "..", "model", "reference_predictions.json");
const reference = JSON.parse(readFileSync(referencePath, "utf-8"));

let allMatch = true;
let maxDiff = 0.0;
let count = 0;

console.log(
  "Matn".padEnd(60) + "sklearn".padEnd(22) + "javascript".padEnd(22) + "MOS?"
);
console.log("-".repeat(120));

for (const [text, ref] of Object.entries(reference)) {
  const result = predict(text, wordFeatures, charFeatures, modelConfig);
  const jsProbaForRefClass = result.proba[ref.predicted];
  const skProbaForRefClass = ref.predicted === "phishing" ? ref.proba_phishing : ref.proba_safe;

  const diff = Math.abs(jsProbaForRefClass - skProbaForRefClass);
  maxDiff = Math.max(maxDiff, diff);

  const match = result.predicted === ref.predicted && diff < 0.001;
  allMatch = allMatch && match;
  count++;

  const short = text.length > 55 ? text.slice(0, 55) + "..." : text;
  const skStr = `${ref.predicted} (${skProbaForRefClass.toFixed(4)})`;
  const jsStr = `${result.predicted} (${jsProbaForRefClass.toFixed(4)})`;
  const mark = match ? "✅" : "❌ FARQ BOR!";

  console.log(short.padEnd(60) + skStr.padEnd(22) + jsStr.padEnd(22) + mark);
}

console.log("-".repeat(120));
console.log(`\nJami tekshirilgan: ${count} ta`);
console.log(`Maksimal ehtimollik farqi: ${maxDiff.toFixed(6)}`);
if (allMatch) {
  console.log("✅ NATIJA: Barcha holatlarda MOS KELDI. Production kod (.mjs) to'g'ri ishlaydi.");
} else {
  console.log("❌ NATIJA: FARQLAR TOPILDI!");
  process.exit(1);
}
