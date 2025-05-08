from server import serve

def main():
    import argparse
    import asyncio


    parser = argparse.ArgumentParser(
        description="Please provide a Resend API key."
    )   
    
    parser.add_argument("--api-key", type=str, help="Resend API key")
    parser.add_argument("--domain", type=str, help="Domain to send email to")

    args = parser.parse_args()

    asyncio.run(serve(args.api_key, args.domain))


if __name__ == "__main__":
    main()
