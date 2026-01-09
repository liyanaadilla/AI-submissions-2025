import { NextResponse } from 'next/server';

// --- IMPROVED SYSTEM PROMPT ---
const SYSTEM_PROMPT = `
You are an expert architectural AI. Your task is to analyze 2D floor plan images and convert them into a structured JSON format for a web app.

**CRITICAL: SCALING & DIMENSIONING STRATEGY**
1.  **Find a Reference:** Look for a standard single door. **ASSUME the door width is 915mm.**
2.  **Calculate Scale:** Use this 915mm reference to determine the pixel-to-millimeter ratio of the image.
3.  **Apply Scale:** Convert ALL other detected lengths and positions into MILLIMETERS (mm) based on this ratio.
4.  **Detect Room Sizes:** If you see text labels like "3000" or "3m", prioritize those values over your visual estimate.

**Output Format (JSON Only):**
{
  "width": number, // The TOTAL bounding box width of the detected plan + 2000mm padding
  "height": number, // The TOTAL bounding box height of the detected plan + 2000mm padding
  "rooms": [
    { 
      "id": "r1", 
      "type": "room", 
      "roomType": "Office" | "Habitable" | "Bedroom" | "Living", 
      "x": number, "y": number, "width": number, "height": number, 
      "area": number, // Calculate: (width * height) / 1,000,000
      "ceilingHeight": 2400 
    }
  ],
  "doors": [
    { 
      "id": "d1", 
      "type": "door", 
      "x": number, "y": number, 
      "width": 915, // Default to 915 unless clearly double doors
      "height": 40, 
      "rotation": 0 | 90 | 180 | 270, 
      "swingDirection": "LH" | "RH", 
      "isRequiredExit": boolean 
    }
  ],
  "fixtures": [
    {
      "id": "f1",
      "type": "fixture",
      "name": "Sink" | "Toilet" | "Shower",
      "x": number, "y": number,
      "width": number, "height": number,
      "isAccessible": true,
      "clearanceWidth": 800,
      "clearanceDepth": 1200
    }
  ],
  "paths": []
}

**Detection Rules:**
1.  **Stage Size:** The "width" and "height" in the root JSON must be large enough to contain all rooms. Do not default to 0.
2.  **Fixtures:** You MUST detect sinks (rectangle ~500x500mm), toilets (oval ~400x700mm), and showers.
3.  **Coordinate System:** Top-Left is (0,0). Ensure objects are placed positively (x > 0, y > 0).
4.  **Accuracy:** Align rooms so walls touch where appropriate.
`;

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const apiKey = process.env.OPENAI_API_KEY;

    // --- OPTION A: MOCK MODE (Fallback if no API Key) ---
    if (!apiKey) {
      console.warn("⚠️ No OPENAI_API_KEY found. Using Enhanced Mock Data.");
      
      await new Promise(resolve => setTimeout(resolve, 2000)); 
      
      // Improved Mock Data that demonstrates "fitting the stage"
      return NextResponse.json({
        width: 8000,  // Auto-sized to fit the content
        height: 6000,
        rooms: [
          { id: `ai-r1`, type: 'room', roomType: 'Office', x: 1000, y: 1000, width: 4000, height: 3000, area: 12, ceilingHeight: 2500 },
          { id: `ai-r2`, type: 'room', roomType: 'Habitable', x: 5000, y: 1000, width: 2000, height: 3000, area: 6, ceilingHeight: 2500 }
        ],
        doors: [
          { id: `ai-d1`, type: 'door', x: 4500, y: 1000, width: 915, height: 40, rotation: 0, swingDirection: 'LH', isRequiredExit: true }
        ],
        fixtures: [
          { id: `ai-f1`, type: 'fixture', name: 'Sink', x: 1200, y: 1200, width: 500, height: 500, isAccessible: true, clearanceWidth: 800, clearanceDepth: 1200 }
        ],
        paths: []
      });
    }

    // --- OPTION B: REAL AI IMPLEMENTATION ---
    const buffer = await file.arrayBuffer();
    const base64Image = Buffer.from(buffer).toString('base64');

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o", 
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { 
            role: "user", 
            content: [
              { type: "text", text: "Analyze this floor plan image. Scale it assuming standard doors are 915mm. Return the JSON layout." },
              { type: "image_url", image_url: { url: `data:image/jpeg;base64,${base64Image}`, detail: "high" } }
            ] 
          }
        ],
        response_format: { type: "json_object" },
        temperature: 0.2 // Lower temp = more precise math/JSON
      })
    });

    if (!response.ok) {
      const errData = await response.json();
      console.error("OpenAI API Error:", errData);
      throw new Error(`OpenAI API failed: ${errData.error?.message || response.statusText}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content;
    
    if (!content) throw new Error("No content received from AI");

    const plan = JSON.parse(content);
    return NextResponse.json(plan);

  } catch (error: any) {
    console.error('AI Analysis Failed:', error);
    return NextResponse.json({ error: error.message || 'Failed to analyze plan' }, { status: 500 });
  }
}