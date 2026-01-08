import { GoogleGenAI, Type } from "@google/genai";
import { ProcessingResult } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const SYSTEM_INSTRUCTION = `
You are the AI engine for the "Smart Document Digitization Platform". 
Your goal is to digitize physical documents, extract information, and validate it using specific Knowledge Representation rules.

**Process:**
1. **OCR & Recognition:** Extract ALL text from the image verbatim as 'rawText'. Identify if text is printed or handwritten.
2. **Document Classification:** Identify if it is an Invoice, ID Card, Receipt, Letter, or Other.
3. **Data Extraction:** Extract key fields relevant to the document type.
4. **Knowledge Representation (Validation Rules):**
   - **Document Type Identification:** If document has 'company_name' AND 'invoice number' AND 'total amount', it is an 'Invoice'.
   - **Date Validation:** Check if dates match 'DD/MM/YYYY'. If not, flag as validation error.
   - **Language Detection:** If most words are Malay, set language to 'Malay'.
   - **Consistency Check:** If 'Invoice', it MUST have a 'Total Amount'. If missing, flag as incomplete.
   - **Confidence Check:** If handwriting is detected or text is blurry, lower the confidence score.

**Risk Degree Logic (Calculate this for the output):**
- **High (Risk III):** Validation rules failed (e.g., missing total on invoice, bad date format).
- **Medium (Risk II):** Low OCR confidence (< 0.7) or handwritten text detected.
- **Low (Risk I/None):** Clean printed text, all rules passed.

Return the result strictly in JSON format.
`;

export const analyzeDocument = async (base64Image: string): Promise<ProcessingResult> => {
  const model = "gemini-2.5-flash-lite"; 

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: "image/jpeg",
              data: base64Image
            }
          },
          {
            text: "Analyze this document based on the system instructions. Extract fields, validate them, and determine the risk degree."
          }
        ]
      },
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            documentType: { type: Type.STRING },
            language: { type: Type.STRING },
            summary: { type: Type.STRING },
            overallConfidence: { type: Type.NUMBER, description: "0.0 to 1.0" },
            riskDegree: { type: Type.STRING, enum: ["Low", "Medium", "High"] },
            rawText: { type: Type.STRING, description: "The full unformatted text content extracted from the document." },
            fields: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  key: { type: Type.STRING },
                  value: { type: Type.STRING },
                  confidence: { type: Type.NUMBER },
                  validationError: { type: Type.STRING, nullable: true }
                },
                required: ["key", "value", "confidence"]
              }
            }
          },
          required: ["documentType", "language", "fields", "riskDegree", "overallConfidence", "rawText"]
        }
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");

    return JSON.parse(text) as ProcessingResult;

  } catch (error) {
    console.error("Gemini Analysis Failed:", error);
    throw error;
  }
};