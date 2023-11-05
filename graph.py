"""A sample script to generate a Sankey diagram for Instant Runoff Voting."""
import plotly.graph_objects as go

def generate_sankey(transfer_log, candidates):
    # Add nodes for the initial round
    nodes = [{"name": f"Round 0 {candidate}"} for candidate in candidates]
    
    # Add nodes for the subsequent rounds
    nodes.extend([{"name": f"Round {round_num} {candidate}"} for round_num, round_data in transfer_log.items() for candidate in round_data.keys()])
    
    labels = [node["name"] for node in nodes]
    
    sources = []
    targets = []
    values = []
    
    for round_num, round_data in transfer_log.items():
        for candidate, votes in round_data.items():
            current_index = labels.index(f"Round {round_num} {candidate}")
            for vote_source, transferred_votes in votes.items():
                if transferred_votes > 0:
                    source_index = labels.index(f"Round {round_num-1} {vote_source}")
                    sources.append(source_index)
                    targets.append(current_index)
                    values.append(transferred_votes)

    fig = go.Figure(go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = labels
        ),
        link = dict(
            source = sources,
            target = targets,
            value = values
        )
    ))

    fig.update_layout(title_text="Instant Runoff Voting Flow", font_size=10)
    fig.show()

# Sample transfer_log to be used for demonstration
transfer_log = {
    2: {
        'A': {'A': 40, 'B': 10},
        'B': {'B': 35, 'C': 5},
        'C': {'A': 3, 'C': 7}
    },
    3: {
        'A': {'A': 43, 'B': 7},
        'B': {'B': 40, 'C': 0},
    }
}

candidates = ['A', 'B', 'C']

generate_sankey(transfer_log, candidates)
