# Efficient Data Stream Anomaly Detection

This project implements real-time anomaly detection in a simulated data stream using a moving average algorithm with a dynamic threshold.

## Algorithm: Moving Average with Dynamic Threshold

**Explanation and Effectiveness:** This algorithm calculates a moving average of recent data points within a specified window. A dynamic threshold is then calculated based on the standard deviation within that window. An anomaly is flagged if the current data point exceeds this threshold.  This approach is effective for several reasons:

* **Adaptability:** The dynamic threshold adapts to changing data patterns and data spread, making it more robust than a fixed threshold.
* **Efficiency:**  It's computationally efficient and suitable for real-time detection.
* **Concept Drift Handling:** It handles concept drift reasonably well because the moving window focuses on recent data, allowing the algorithm to adjust to gradual shifts in the baseline.

## Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Run the script:**
   ```bash
   python anomaly_detection.py 
   ```