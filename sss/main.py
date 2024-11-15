import argparse
from sss.shea256_secret_sharing.secretsharing import PlaintextToHexSecretSharer


def split_secret(secret, threshold, shares):
    """Split the secret into shares using Shamir's Secret Sharing scheme."""
    return PlaintextToHexSecretSharer.split_secret(secret, threshold, shares)


def recover_secret(shares):
    """Recover the secret from shares using Shamir's Secret Sharing scheme."""
    return PlaintextToHexSecretSharer.recover_secret(shares)


def main():
    parser = argparse.ArgumentParser(
        description="Split or recover a secret using Shamir's Secret Sharing scheme."
    )

    # Mode selection: split or recover
    parser.add_argument(
        "mode",
        choices=["split", "recover"],
        help="Mode of operation: 'split' to create shares, 'recover' to reconstruct the secret from shares",
    )

    # Arguments for split mode
    parser.add_argument(
        "-is",
        "--input-secret",
        type=str,
        default="secret",
        help="Path to input-file with secrets that needs to be shared.",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=2,
        help="The minimum number of shares needed to reconstruct the secret. Default is 2.",
    )
    parser.add_argument(
        "-n",
        "--num_shares",
        type=int,
        default=5,
        help="The total number of shares to generate. Default is 5.",
    )
    parser.add_argument(
        "-osh",
        "--output-shards",
        type=str,
        default="shared_secrets",
        help="Path (with filename suffix) to output file which will contain shares, will generate multiple numbered files. E.g. if 'shared_secret' is provided, then multiple 'shared_secret_\d+' will be generated.",
    )

    # Arguments for recover mode
    parser.add_argument(
        "-ish",
        "--input-shards",
        type=str,
        default="shared_secrets",
        help="Path (with filename suffix) of input file containing shared-secrets. E.g. if 'shared_secret' is provided, then all 'shared_secret_\d+' would be consumed from that path.",
    )
    parser.add_argument(
        "-os",
        "--output-secret",
        type=str,
        default=None,
        help="Path to output file containing the recovered secret.",
    )

    args = parser.parse_args()

    if args.mode == "split":
        # Split mode
        if args.input_secret is None:
            print("Error: Secret must be provided in split mode.")
            return
        shares = split_secret(args.secret, args.threshold, args.num_shares)
        print("Shares generated:")
        for i, share in enumerate(shares, start=1):
            print(f"Share {i}: {share}")

    elif args.mode == "recover":
        # Recover mode
        if args.file is None:
            print("Error: File containing shares must be provided in recover mode.")
            return
        # Read shares from file
        try:
            with open(args.file, "r") as f:
                shares = [line.strip() for line in f if line.strip()]
            if len(shares) < 2:
                print("Error: At least 2 shares are required to recover the secret.")
                return
            secret = recover_secret(shares)
            print(f"Recovered Secret: {secret}")
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")


if __name__ == "__main__":
    main()
