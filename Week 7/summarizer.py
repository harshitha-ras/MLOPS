import argparse
import sys
import ollama


def summarize_text(text, model="tinyllama"):
    prompt = f"Summarize the following text:\n\n{text}\n\nSummary:"
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Summarize text using TinyLlama via Ollama.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--string", type=str, help="Text string to summarize.")
    group.add_argument("-t", "--textfile", type=str, help="Path to text file to summarize.")
    args = parser.parse_args()

    if args.string:
        input_text = args.string
    elif args.textfile:
        try:
            with open(args.textfile, "r", encoding="utf-8") as f:
                input_text = f.read()
        except FileNotFoundError:
            print("Error: File not found.")
            sys.exit(1)
    else:
        print("Error: No input provided.")
        sys.exit(1)

    summary = summarize_text(input_text)
    print("\nSummary:\n", summary)

if __name__ == "__main__":
    main()
