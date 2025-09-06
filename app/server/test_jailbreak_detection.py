import pandas as pd
import asyncio
import logging
from main import init_gemini, load_agents, agent_manager
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Path to the CSV file
CSV_FILE_PATH = "data/classified_prompts.csv"

# Chunk size for reading the CSV file
CHUNK_SIZE = 1000

async def test_jailbreak_detection():
    """Test the jailbreak detection using the CSV file."""
    # Initialize the Gemini model and agents
    gemini_model = init_gemini()
    if not gemini_model:
        logger.error("Failed to initialize Gemini model")
        return

    load_agents()
    if not agent_manager.agents or not agent_manager.judge:
        logger.error("Failed to initialize agents")
        return

    # Lists to store predictions and labels
    predictions = []
    labels = []

    # Read the CSV file in chunks
    for chunk in pd.read_csv(CSV_FILE_PATH, chunksize=CHUNK_SIZE):
        for _, row in chunk.iterrows():
            prompt = row['prompt']
            label = row['label']

            # Get the council's verdict
            council_decision = await agent_manager.analyze_prompt(prompt)
            verdict = council_decision['verdict']

            # Convert the verdict to a binary label (1 for "Not Permitted", 0 for "Permitted")
            prediction = 1 if "Not Permitted" in verdict else 0

            # Convert the label to a binary label (1 for "jailbreak", 0 for "not_jailbreak")
            true_label = 1 if label == "jailbreak" else 0

            # Append the prediction and label to the lists
            predictions.append(prediction)
            labels.append(true_label)

            # Log the result
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Council's verdict: {verdict}")
            logger.info(f"Expected label: {label}")
            logger.info(f"Prediction: {prediction}")
            logger.info(f"True label: {true_label}")
            logger.info("-" * 50)

    # Calculate metrics
    accuracy = accuracy_score(labels, predictions)
    precision = precision_score(labels, predictions)
    recall = recall_score(labels, predictions)
    f1 = f1_score(labels, predictions)
    conf_matrix = confusion_matrix(labels, predictions)

    # Log the metrics
    logger.info("Metrics:")
    logger.info(f"Accuracy: {accuracy}")
    logger.info(f"Precision: {precision}")
    logger.info(f"Recall: {recall}")
    logger.info(f"F1 Score: {f1}")
    logger.info(f"Confusion Matrix:\n{conf_matrix}")

if __name__ == "__main__":
    asyncio.run(test_jailbreak_detection()) 