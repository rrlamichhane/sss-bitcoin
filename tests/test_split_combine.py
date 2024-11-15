import pytest
import subprocess
from unittest.mock import patch, mock_open
from io import StringIO


@pytest.mark.parametrize(
    "secret_content,threshold,num_shares",
    [
        pytest.param("HelloWorld", 2, 5, id="threshold2_numshares5_simple"),
        pytest.param("PythonTesting123", 3, 5, id="threshold3_numshares5_alphanumeric"),
        pytest.param(
            "ThisIsASecretMessage", 3, 6, id="threshold3_numshares6_longer_text"
        ),
        pytest.param(
            "🤫 Secrets with emoji!", 2, 3, id="threshold2_numshares3_with_emoji"
        ),
    ],
)
@patch("builtins.open", new_callable=mock_open)
@patch(
    "os.path.exists", side_effect=lambda path: True if "secret.txt" in path else False
)
@patch("os.makedirs")
def test_split_and_combine(
    mock_makedirs, mock_exists, mock_file, secret_content, threshold, num_shares
):
    # Step 1: Prepare secret in memory as the input_file "secret.txt"
    # Set up the mock to return the secret content when reading "secret.txt"
    mock_file.return_value.read.return_value = secret_content

    # Run the split command
    split_command = [
        "python",
        "sss/main.py",
        "split",
        "--input-file",
        "secret.txt",
        "--threshold",
        str(threshold),
        "--num-shares",
        str(num_shares),
        "--directory",
        "shares",
    ]

    # Run the command
    result_split = subprocess.run(
        split_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Check if the command was successful
    assert result_split.returncode == 0, f"Splitting failed: {result_split.stderr}"

    # Extract shares from the mocked file write calls for share files
    share_files_content = {}
    for call_args in mock_file.call_args_list:
        if len(call_args[0]) > 0 and "share_" in call_args[0][0]:
            filename = call_args[0][0]
            # The content is written via mock_file().write(...)
            handle = mock_file()
            share_content = handle.write.call_args[0][0].strip()
            share_files_content[filename] = share_content

    assert (
        len(share_files_content) == num_shares
    ), f"Expected {num_shares} shares, got {len(share_files_content)}."

    # Step 2: Combine shares using the first `threshold` shares
    mock_file.reset_mock()  # Reset mock calls for combine operation

    share_files_to_use = sorted(list(share_files_content.keys()))[:threshold]
    combine_command = [
        "python",
        "sss/main.py",
        "combine",
        "-o",
        "recovered_secret.txt",
    ] + share_files_to_use

    # Mock the content of share files to return share data
    def side_effect_combine(path, *args, **kwargs):
        if "share_" in path:
            # Return the content of the share file
            return StringIO(share_files_content[path])
        else:
            # For recovered_secret.txt
            return mock_open()()

    with patch("builtins.open", side_effect=side_effect_combine):
        result_combine = subprocess.run(
            combine_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    # Check if the combine command was successful
    assert result_combine.returncode == 0, f"Combining failed: {result_combine.stderr}"

    # Extract recovered secret from what was written to recovered_secret.txt
    handle = mock_file()
    recovered_secret = handle.write.call_args[0][0] if handle.write.call_args else None
    assert (
        recovered_secret == secret_content
    ), f"Recovered secret did not match original. Expected: {secret_content}, Got: {recovered_secret}"


@pytest.mark.parametrize(
    "threshold,num_shares,expected_error",
    [
        pytest.param(
            3,
            2,
            "Threshold must be < the total number of points.",
            id="threshold_greater_than_shares",
        )
    ],
)
@patch("builtins.open", new_callable=mock_open, read_data="TestSecret")
@patch(
    "os.path.exists", side_effect=lambda path: True if "secret.txt" in path else False
)
@patch("os.makedirs")
def test_error_conditions(
    mock_makedirs, mock_exists, mock_file, threshold, num_shares, expected_error
):
    """Test error conditions for the split command."""
    split_command = [
        "python",
        "sss/main.py",
        "split",
        "--input-file",
        "secret.txt",
        "--threshold",
        str(threshold),
        "--num-shares",
        str(num_shares),
    ]

    result = subprocess.run(
        split_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # Expect an error
    assert result.returncode != 0, "Expected non-zero exit code for invalid parameters."
    assert (
        expected_error in result.stderr
    ), f"Expected error message '{expected_error}' not found in stderr."
