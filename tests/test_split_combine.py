import pytest
import sss
from secret_manager import split_secret, combine_shares

# Utility function to generate a "secret" integer from a list of words (for testing)
def generate_secret(words):
    return int(''.join(str(hash(word))[-4:] for word in words))

# Test cases for `split_secret` function
@pytest.mark.parametrize("words, total_shares, threshold", [
    pytest.param((["word_" + i for i in range(1,13)], 5, 3), id = "12 words, 5 shares, 3 threshold"),
    pytest.param((["word_" + i for i in range(1,13)], 6, 3), id = "12 words, 6 shares, 3 threshold"),
    pytest.param((["word_" + i for i in range(1,25)], 12, 6),  id = "24 words, 12 shares, 6 threshold"),
    pytest.param((["word_" + i for i in range(1,25)], 12, 6),  id = "24 words, 6 shares, 3 threshold"),
    pytest.param((["word_" + i for i in range(1,9)], 4, 4),  id = "8 words, 4 shares, 4 threshold"),
    pytest.param((["word_" + i for i in range(1,9)], 4, 1),  id = "8 words, 4 shares, 1 threshold"),
    pytest.param((["word_" + i for i in range(1,9)], 8, 2),  id = "8 words, 8 shares, 2 threshold"),
    pytest.param((["word_" + i for i in range(1,4)], 3, 2),  id = "3 words, 3 shares, 2 threshold"),
])
def test_split_and_combine(words, total_shares, threshold):
    # Generate the "secret" based on the words
    secret = generate_secret(words)

    # Split the secret into shares
    shares = sss.make_random_shares(secret, threshold, total_shares)
    
    # Check that the correct number of shares was created
    assert len(shares) == total_shares

    # Try to recover the secret with the minimum threshold of shares
    recovered_secret = sss.recover_secret(shares[:threshold])
    assert recovered_secret == secret

    # Try to recover the secret with a different set of shares
    recovered_secret_different_set = sss.recover_secret(shares[-threshold:])
    assert recovered_secret_different_set == secret

    # Edge case: Try with more than threshold shares to ensure they also reconstruct correctly
    if total_shares > threshold:
        recovered_secret_more_shares = sss.recover_secret(shares[:threshold + 1])
        assert recovered_secret_more_shares == secret

# Corner case testing for exact threshold requirement
@pytest.mark.parametrize("words, total_shares, threshold", [
    pytest.param((["corner_" + i for i in range(1,4)], 5, 2),  id = "Secret requires only 2 shares to reconstruct"),
    pytest.param((["boundary_" + i for i in range(1,11)], 7, 4),  id = "Secret with more shares than required for threshold"),
])
def test_corner_cases(words, total_shares, threshold):
    # Generate the secret from the given words
    secret = generate_secret(words)

    # Generate shares
    shares = sss.make_random_shares(secret, threshold, total_shares)

    # Verify that exactly `threshold` shares can reconstruct the secret
    recovered_secret = sss.recover_secret(shares[:threshold])
    assert recovered_secret == secret

    # Ensure all shares can reconstruct the secret as well
    recovered_secret_all_shares = sss.recover_secret(shares)
    assert recovered_secret_all_shares == secret

    # Verify that using fewer than the threshold raises an error
    if threshold > 1:
        with pytest.raises(ValueError, match="need at least"):
            sss.recover_secret(shares[:threshold - 1])

# Edge case: Extremely high threshold (all shares required)
@pytest.mark.parametrize("words", [
    pytest.param((["edge_case_" + i for i in range(1, 13)), id="12 words, high threshold"),
    pytest.param((["edge_case_" + i for i in range(1, 25)), id="24 words, high threshold"),
])
def test_high_threshold(words):
    secret = generate_secret(words)
    total_shares = len(words)
    threshold = total_shares  # Require all shares

    shares = sss.make_random_shares(secret, threshold, total_shares)
    
    # Try to reconstruct with all shares (since threshold equals total shares)
    recovered_secret = sss.recover_secret(shares)
    assert recovered_secret == secret

    # Try reconstructing with one fewer than total shares (should fail)
    with pytest.raises(ValueError, match="need at least"):
        sss.recover_secret(shares[:-1])
