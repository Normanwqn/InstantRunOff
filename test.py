import plotly.graph_objects as go

# Hypothetical ranked voting data
ballots = [
    ["Alice", "Bob", "Charlie"],
    ["Charlie", "Alice", "Bob"],
    ["Bob", "Alice", "Charlie"],
]

# Extract unique candidate names
unique_candidates = list(set(candidate for ballot in ballots for candidate in ballot))

# Create a dictionary to count the flow of votes
vote_flows = {(source, target): 0 for source in unique_candidates for target in unique_candidates}

# Count the flow of votes from each candidate to each candidate
for ballot in ballots:
    for i in range(len(ballot) - 1):
        source = ballot[i]
        target = ballot[i + 1]
        vote_flows[(source, target)] += 1

# Create a Sankey diagram
sankey_fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=unique_candidates,
    ),
    link=dict(
        source=[unique_candidates.index(source) for (source, target) in vote_flows.keys()],
        target=[unique_candidates.index(target) for (source, target) in vote_flows.keys()],
        value=list(vote_flows.values()),
    ),
))

# Show the Sankey chart
sankey_fig.show()

