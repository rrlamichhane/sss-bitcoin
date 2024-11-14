import argparse
import os
import shamirs_secret_sharing as sss

def split_secret(input_file, output_dir, total_shares=6, threshold=3):
    # Read the secret from the input file
    with open(input_file, "r") as f:
        secret = int(f.read().strip())  # Expecting a numeric secret
    
    # Generate the shares using sss.make_random_shares
    shares = sss.make_random_shares(secret, threshold, total_shares)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each share to a separate file
    for i, share in enumerate(shares):
        share_file = os.path.join(output_dir, f"share{i + 1}.txt")
        with open(share_file, "w") as f:
            f.write(f"{share[0]},{share[1]}\n")
        print(f"Share {i + 1} saved to {share_file}")
    
    print(f"Successfully split the secret into {total_shares} shares with a threshold of {threshold}.")

def combine_shares(share_files):
    # Load shares from provided files
    shares = []
    for file_path in share_files:
        with open(file_path, "r") as f:
            x, y = map(int, f.read().strip().split(","))
            shares.append((x, y))
    
    # Recover the secret using sss.recover_secret
    secret = sss.recover_secret(shares)
    print("Reconstructed Secret:", secret)

def main():
    parser = argparse.ArgumentParser(description="Shamir's Secret Sharing Manager")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Split command
    split_parser = subparsers.add_parser("split", help="Split a secret into shares")
    split_parser.add_argument("-i", "--input-file", type=str, required=True,
                              help="Path to the input file containing the secret (numeric)")
    split_parser.add_argument("-o", "--output-dir", type=str, default="./shares",
                              help="Directory to save the generated shares (default: ./shares)")
    split_parser.add_argument("-n", "--total-shares", type=int, default=6,
                              help="Total number of shares to create (default: 6)")
    split_parser.add_argument("-t", "--threshold", type=int, default=3,
                              help="Minimum number of shares required to reconstruct the secret (default: 3)")

    # Combine command
    combine_parser = subparsers.add_parser("combine", help="Combine shares to reconstruct the secret")
    combine_parser.add_argument("share_files", nargs="+", type=str,
                                help="Paths to share files to combine for reconstruction")
    
    args = parser.parse_args()
    
    if args.command == "split":
        split_secret(args.input_file, args.output_dir, args.total_shares, args.threshold)
    elif args.command == "combine":
        combine_shares(args.share_files)

if __name__ == "__main__":
    main()
