/**
 * CyberShield AI — sof JavaScript (hech qanday tashqi ML kutubxonasiz) bashorat moduli.
 *
 * Bu fayl Python'dagi model/pure_predict.py bilan MATEMATIK JIHATDAN AYNAN bir xil
 * hisoblashni amalga oshiradi:
 *   1. Matnni normalizatsiya (apostrof variantlari, kichik harf)
 *   2. So'z tokenlari (regex: kamida 2 harfdan iborat so'zlar) + 1-2 gramlar
 *   3. Harf 2-5 gramlari (so'z chegaralari ichida, char_wb uslubida)
 *   4. TF-IDF (sublinear_tf: 1 + log(count)) + L2 normalizatsiya
 *   5. Logistic Regression: chiziqli yig'indi + intercept -> sigmoid
 *
 * Netlify Functions'da ishlatilishi uchun mo'ljallangan — hech qanday
 * tashqi npm paketi kerak emas, faqat Node.js o'zining standart imkoniyatlari.
 */

const APOSTROPHE_VARIANTS = ["\u0027", "\u0027", "\u02BB", "\u02BC", "\u0060", "\u00B4", "\u2018"];

function normalizeText(text) {
  let result = String(text);
  for (const variant of APOSTROPHE_VARIANTS) {
    result = result.split(variant).join("'");
  }
  result = result.toLowerCase();
  result = result.replace(/\s+/g, " ").trim();
  return result;
}

// sklearn'ning standart so'z token patterni: (?u)\b\w\w+\b
// JS regex'da \w unicode harflarni to'liq qamrab olmaydi, shuning uchun
// unicode-aware qo'lda pattern ishlatamiz (lotin + kirill harflar + raqamlar + pastki chiziq).
const WORD_TOKEN_PATTERN = /[\p{L}\p{N}_]{2,}/gu;
// Eslatma: sklearn \b\w\w+\b "kamida 2 belgili ketma-ket \w" degani, chegaralar bilan.
// Yuqoridagi pattern buni funksional jihatdan takrorlaydi (unicode harf/raqam/pastki chiziq
// ketma-ketligi, kamida 2 belgi).

function wordTokenize(text) {
  const matches = text.match(WORD_TOKEN_PATTERN);
  return matches || [];
}

function wordNgrams(tokens, ngramRange) {
  const [minN, maxN] = ngramRange;
  const ngrams = [];
  const nTokens = tokens.length;
  for (let n = minN; n <= Math.min(maxN, nTokens); n++) {
    for (let i = 0; i <= nTokens - n; i++) {
      ngrams.push(tokens.slice(i, i + n).join(" "));
    }
  }
  return ngrams;
}

function charWbNgrams(text, ngramRange) {
  const cleaned = text.replace(/\s+/g, " ");
  const [minN, maxN] = ngramRange;
  const ngrams = [];
  for (const word of cleaned.split(" ")) {
    if (word.length === 0) continue;
    const w = " " + word + " ";
    const wLen = w.length;
    for (let n = minN; n <= Math.min(maxN, wLen); n++) {
      let offset = 0;
      ngrams.push(w.slice(offset, offset + n));
      while (offset + n < wLen) {
        offset += 1;
        ngrams.push(w.slice(offset, offset + n));
      }
      if (offset === 0) break;
    }
  }
  return ngrams;
}

function tfidfWeightedSum(ngrams, featuresDict) {
  const counts = {};
  for (const ng of ngrams) {
    if (featuresDict.hasOwnProperty(ng)) {
      counts[ng] = (counts[ng] || 0) + 1;
    }
  }

  const keys = Object.keys(counts);
  if (keys.length === 0) return 0.0;

  const rawTfidf = {};
  for (const ng of keys) {
    const [idf] = featuresDict[ng];
    const tf = 1.0 + Math.log(counts[ng]); // sublinear_tf=True
    rawTfidf[ng] = tf * idf;
  }

  let sumSquares = 0.0;
  for (const ng of keys) sumSquares += rawTfidf[ng] * rawTfidf[ng];
  const l2Norm = Math.sqrt(sumSquares);
  if (l2Norm === 0) return 0.0;

  let weightedSum = 0.0;
  for (const ng of keys) {
    const normalized = rawTfidf[ng] / l2Norm;
    const [, coef] = featuresDict[ng];
    weightedSum += normalized * coef;
  }
  return weightedSum;
}

/**
 * @param {string} text - tahlil qilinadigan matn
 * @param {object} wordFeatures - {token: [idf, coef]}
 * @param {object} charFeatures - {ngram: [idf, coef]}
 * @param {object} config - {intercept, classes, word_ngram_range, char_ngram_range}
 * @returns {{predicted: string, proba: {[key: string]: number}}}
 */
function predict(text, wordFeatures, charFeatures, config) {
  const normalized = normalizeText(text);

  const tokens = wordTokenize(normalized);
  const ngramsWord = wordNgrams(tokens, config.word_ngram_range);
  const ngramsChar = charWbNgrams(normalized, config.char_ngram_range);

  const wordSum = tfidfWeightedSum(ngramsWord, wordFeatures);
  const charSum = tfidfWeightedSum(ngramsChar, charFeatures);

  const decision = wordSum + charSum + config.intercept;

  const pSafe = 1.0 / (1.0 + Math.exp(-decision));
  const pPhishing = 1.0 - pSafe;

  const [classPhishing, classSafe] = config.classes; // ['phishing', 'safe']
  const proba = { [classPhishing]: pPhishing, [classSafe]: pSafe };
  const predicted = pSafe > pPhishing ? classSafe : classPhishing;

  return { predicted, proba };
}

export { predict, normalizeText, wordTokenize, wordNgrams, charWbNgrams };
