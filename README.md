# Text to Brainrot

This app takes content as input and sends it to OpenAI's API, generating a summary in the "brainrot" style. Why? Because my brain is fried, and complex/dry content is more easily understood when it has subway surfers footage + meme style delivery.

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

3. Wait as the app extracts text and sends it to OpenAI.

4. Enjoy your brainrot-style summary!

## Example

Original PDF content: *"A comprehensive analysis of macroeconomic factors affecting GDP..."*

Brainrot-style summary: *"Basically, it’s like this: the economy goes up, it goes down. GDP loves that. Repeat cycle."*

## Contributing

Contributions are welcome! If you have ideas for improving the app or making the summaries even more "brainrot," feel free to submit a pull request.

## License

This project is licensed under the MIT License.
