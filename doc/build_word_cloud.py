import matplotlib.pyplot as plt
import pylab
import requests
from pylab import savefig
from tqdm import tqdm
from wordcloud import WordCloud

import damona


def fetch_biotools_metadata(tool_name):
    """Fetch metadata for a given tool from bio.tools API."""
    url = f"https://bio.tools/api/tool/{tool_name}?format=json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        # print(f"Error fetching {tool_name}: {response.status_code}")
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
    # plt.show()


reg = damona.registry.Registry()

# look at all binaries and tools' names
# First tools only
all_keywords = []
found = 0
tools = set([y for x in reg.registry.values() for y in x.binaries])
tools = set([x.split(":")[0] for x in reg.get_list()])
print(f"Introspecting {len(tools)} tools on bio.tools")
for tool in tqdm(list(tools)):
    data = fetch_biotools_metadata(tool)
    if data:
        all_keywords += extract_keywords(data)
        found += 1
generate_tag_cloud(all_keywords)
print(f"Scanned {len(tools)}; found {found}")
savefig("wordcloud_tools.png")

# then binaries only
all_keywords = []
found = 0
tools = set([y for x in reg.registry.values() for y in x.binaries])
print(f"Introspecting {len(tools)} binaries on bio.tools")
for tool in tqdm(list(tools)):
    data = fetch_biotools_metadata(tool)
    if data:
        all_keywords += extract_keywords(data)
        found += 1
generate_tag_cloud(all_keywords)
print(f"Scanned {len(tools)}; found {found}")
savefig("wordcloud_binaries.png")
