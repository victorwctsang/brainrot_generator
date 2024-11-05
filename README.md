# Text to Brainrot

This app takes content as input and sends it to OpenAI's API, generating a summary in the "brainrot" style. Why? Because my brain is fried, and complex/dry content is more easily understood when it has subway surfers footage + meme style delivery.

## Example

[Example Video](https://www.canva.com/design/DAGVnKSRMYs/bPv5Fn0w0kUpj66XiqFuIA/watch?utm_content=DAGVnKSRMYs&utm_campaign=designshare&utm_medium=link&utm_source=editor)

## Features

- [x] **Free text input**: Accepts text input.
- [x] **PDF Upload**: Accepts PDF files and extracts the text for processing.
- [x] **OpenAI API Integration**: Sends extracted text to OpenAI’s API to generate a summary.
- [x] **Brainrot Style Output**: Utilizes custom prompt engineering to produce "brainrot"-style summaries—quirky, lighthearted, and engaging.
- [x] **Plain Text Output**: Returns output in text form.
- [x] **Video Output**: The text output will be overlaid on a subway surfers video with AI text to speech.
- [ ] **Fine Tuned Model**: A specific model trained on brainrot responses.
- [ ] **Subtitled Video**: Subtitles to go with the brainrot TTS video.

## Getting Started

### Prerequisites

- Python 3.x
- [OpenAI API Key](https://platform.openai.com/signup/)
- Required libraries: `PyPDF2` (for PDF extraction), `openai` (for API access), and `requests`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/victorwctsang/brainrot_generator.git
   cd brainrot_generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your_api_key_here'
   ```

### Usage

1. Run the app:
   ```bash
   python app.py
   ```

2. Upload a PDF file.

3. Wait as the app extracts text, sends it to OpenAI, and generates the text to speech audio for the subway surfers clip.

4. Enjoy your brainrot-style summary!
