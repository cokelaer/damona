import matplotlib.pyplot as plt
import pylab
import requests
from wordcloud import WordCloud


def fetch_biotools_metadata(tool_name):
    """Fetch metadata for a given tool from bio.tools API."""
    url = f"https://bio.tools/api/tool/{tool_name}?format=json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {tool_name}: {response.status_code}")
        return None


def extract_keywords(tool_data):
    """Extract relevant keywords from bio.tools metadata."""
    keywords = []

    if not tool_data:
        return keywords

    # Extract topics, operations, and other relevant metadata
    if "topic" in tool_data:
        keywords += [topic["term"] for topic in tool_data["topic"]]

    if "operation" in tool_data:
        keywords += [op["term"] for op in tool_data["operation"]]

    return keywords


def generate_tag_cloud(keywords):
    """Generate and display a word cloud from extracted keywords."""
    text = " ".join(keywords)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()


from tqdm import tqdm

import damona

reg = damona.registry.Registry()
tools = set([y for x in reg.registry.values() for y in x.binaries])
all_keywords = []

for tool in tqdm(tools):
    data = fetch_biotools_metadata(tool)
    all_keywords += extract_keywords(data)
generate_tag_cloud(all_keywords)
savefig("wordcloud.png")
