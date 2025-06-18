Text Summarizer CLI Tool
A command-line tool for summarizing text using the locally running TinyLlama model via Ollama on Windows.




Features
- Summarizes text from a string or a file using TinyLlama via Ollama.

- Simple command-line interface with clear options.

- Handles errors gracefully and provides helpful messages.




Requirements
- Windows 10 or later.

- Python 3.8 or higher.

- Ollama installed and running.

- TinyLlama model downloaded via Ollama.

- Python package: ollama.




Installation
1. Install Python:
Download and install Python 3.8+ from python.org.

2. Install Ollama:
Download and install Ollama from ollama.com.

3. Download TinyLlama Model:
Open Command Prompt and run:
ollama pull tinyllama

Ensure Ollama is running.


4. Install requirements.txt by running:
pip install -r requirements.txt

5. Clone the CLI Tool:
Save summarizer.py to your project directory.





Setup
- Ensure Ollama is running before using the tool.

- Verify TinyLlama is available by running:

ollama list

You should see tinyllama in the list.





Usage
Run the tool from the command line:

python summarizer.py -s "Your text here"


OR


python summarizer.py -t path/to/your/file.txt




Options


![alt text](<Cmd Options.png>)





Examples
Summarize a string:



python summarizer.py -s "Artificial intelligence is transforming the world."

![alt text](Results.png)



Summarize a file:



python summarizer.py -t article.txt




Testing
Unit Tests:
Write tests for the summarize_text function using unittest or pytest.

Coverage Report:


Run these coverage commands:
coverage run summarizer.py -s "Test text"
coverage report




Troubleshooting
Ollama Not Running:
Start Ollama from the Start Menu or by running ollama serve in Command Prompt.

Model Not Found:
Run ollama pull tinyllama to download the model.

File Not Found Error:
Check the file path and ensure the file exists.

API/Connection Errors:
Ensure Ollama is running and accessible.


