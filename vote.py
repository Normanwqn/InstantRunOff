import csv
import plotly.graph_objects as go
import argparse
from collections import defaultdict

def number_to_ordinal(n):
    """Convert number to the an ordinal string,"""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix

def ordinal_to_number(ordinal):
    try:
        # Remove the ordinal suffix (e.g., "st", "nd", "rd", "th")
        ordinal = ordinal.rstrip('stndrdth')
        
        # Convert the remaining string to an integer
        return int(ordinal)
    except ValueError:
        raise ValueError(f"{ordinal} Invalid input: Not a valid ordinal number")


def generate_ballot_from_row(row) -> list[int]:
    """Read a row in csv to generate a ranked list of preferences.
    
    e.g. ['1', '2', '3', '4', '5', '6', '7', '8'] means the voter 
    ranked 1 as the first choice, 2 as the second choice, etc.
    """
    preference_ranking = [None] * 8
    for candidate_idx, candidate_preference in enumerate(row):
        if candidate_preference:
            preference_ranking[ordinal_to_number(candidate_preference) - 1] = str(candidate_idx + 1)
    
    preference_ranking = list(filter(lambda x: x is not None, preference_ranking))
    print(preference_ranking)
    return preference_ranking


def generate_ballots_csv(file_name: str) -> list[list[int]]:
    """Generate the ballots from a csv file."""
    def generate_ballots():
        with open(file_name, 'r') as file:
            csv_reader = csv.reader(file)
             # Read the header row to get column names
            _header = next(csv_reader)
            print("Ballots")
            for i, row in enumerate(csv_reader):
                if row:
                    print(row[0], " ", end='')
                    yield generate_ballot_from_row(row[1:])
                
    return list(generate_ballots())

def remove_eliminated_candidates(ballot, eliminated_candidates) -> int:
    """Remove eliminated candidates from the ballots.
    
    Return the first eliminated candidate.
    """
    first_eliminated = ballot[0]
    while ballot[0] in eliminated_candidates:
            ballot.remove(ballot[0])
    return first_eliminated        

def redistribute_votes(ballots, eliminated_candidates, transfer_log, round_num):
    """Redistribute votes from eliminated candidates.
    
    Count the number of votes transferred from each eliminated 
    candidate to each remaining candidate, adding to the transfer log.
    
    Count the number of votes that are not transferred, adding to the transfer log.
    """
    transfer_log[round_num] = defaultdict(dict)
    for ballot in ballots:
        if not ballot:
            continue
        if ballot[0] in eliminated_candidates:
            first_eliminated = remove_eliminated_candidates(ballot, eliminated_candidates)
            
            transfer_log[round_num][ballot[0]][first_eliminated] = transfer_log[round_num][ballot[0]].get(first_eliminated, 0) + 1
        else:
            transfer_log[round_num][ballot[0]][ballot[0]] = transfer_log[round_num][ballot[0]].get(ballot[0], 0) + 1
    

def print_round_results(vote_counts, total_votes, candidate_list):
    """Print the results of the current round."""
    sorted_candidates = sorted(candidate_list, key=lambda c: vote_counts.get(c, 0), reverse=True)
    for candidate in sorted_candidates:
        votes = vote_counts.get(candidate, 0)
        print(f"{candidate}: {votes} vote{'s' if votes != 1 else ''} ({votes / total_votes * 100:.2f}% of total)")
    
    
def produce_vote_counts(ballots, remaining_candidates):
    vote_counts = {candidate: 0 for candidate in remaining_candidates}  # Initialize all vote counts to zero
    for ballot in ballots:
        if ballot:  # If the ballot still has candidates listed
            vote_counts[ballot[0]] += 1
    return vote_counts

def eliminate_candidate(vote_counts, remaining_candidates):
    """Eliminate the candidate with the fewest votes.

    Return the remaining candidates
    """
    min_votes = min(vote_counts.values())
    newly_eliminated_candidates = set()
    for candidate, votes in vote_counts.items():
        if votes == min_votes and candidate in remaining_candidates:
            remaining_candidates.remove(candidate)
            newly_eliminated_candidates.add(candidate)
            
    if len(newly_eliminated_candidates) != 0:
        print("Eliminated candidates: ", end='')
    for candidate in newly_eliminated_candidates:
        print(f"{candidate} ", end='')
    
    return remaining_candidates, newly_eliminated_candidates

def get_winner(ballots, candidate_list):
    """Determine the winner of an instant runoff election."""
    remaining_candidates = set(candidate_list)  # Start with all candidates
    eliminated_candidates = set()
    current_round = 1
    transfer_log = defaultdict(dict)
    while True:
        # Count the votes for each candidate
        vote_counts = produce_vote_counts(ballots, remaining_candidates)
        
        total_votes = sum(vote_counts.values())

        # Print the round results
        print(f"{number_to_ordinal(current_round)} round results:")
        print_round_results(vote_counts, total_votes, remaining_candidates)

        if len(remaining_candidates) == 1: # If only one candidate remains
            return transfer_log, remaining_candidates.pop()
        
        # If any candidate has more than half the votes, they win
        for candidate, votes in vote_counts.items():
            if votes > total_votes / 2:
                return transfer_log, candidate
        
        remaining_candidates, newly_eliminated_candidates = eliminate_candidate(vote_counts, remaining_candidates)
        
        eliminated_candidates.update(newly_eliminated_candidates)

        # If no candidates remain, it's a tie (should not happen with IRV but included for completeness)
        if not remaining_candidates:
            return transfer_log, "Tie"

        # Redistribute votes from eliminated candidates
        # eliminated_candidates = set(candidate_list) - remaining_candidates
        redistribute_votes(ballots, eliminated_candidates, transfer_log, current_round)
        
        current_round += 1
        print()  # Print a newline for better readability

def generate_sankey(transfer_log, candidates, save_file_path, show_figure):
    """Generate a sankey diagram.

    Export to html or show figure as a new webpage.
    """
    # Add nodes for the initial round
    nodes = [{"name": f"Round 0, Candidate {candidate}"} for candidate in candidates]
    
    # Add nodes for the subsequent rounds
    nodes.extend([{"name": f"Round {round_num}, Candidate {candidate}"} for round_num in transfer_log.keys() for candidate in candidates])
    
    labels = [node["name"] for node in nodes]
    
    sources = []
    targets = []
    values = []
    
    for round_num, round_data in transfer_log.items():
        for candidate, votes in round_data.items():
            current_index = labels.index(f"Round {round_num}, Candidate {candidate}")
            for vote_source, transferred_votes in votes.items():
                if transferred_votes > 0:
                    source_index = labels.index(f"Round {round_num-1}, Candidate {vote_source}")
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

    fig.update_layout(title_text="Instant Runoff Voting Flow", font_size=18)
    
    fig.write_html(save_file_path)
    print(f"Sankey diagram saved as {save_file_path}")
    
    if show_figure:
        fig.show()

def main(args):
    """Perform generic Instant Runoff base on ballot.csv.

    Base on the Google Form's auto export.
    """
    num_candidates = 8
    # this can be changed for future votes
    candidate_names = [
        f"{i}" for i in range(1, num_candidates + 1)
    ]
    ballots = generate_ballots_csv(args.input)
    transfer_log, winner = get_winner(ballots, candidate_names)
    print(f"\nWinner is {winner}")
    generate_sankey(transfer_log, candidate_names, save_file_path=args.output, show_figure=args.show)

if __name__ == "__main__":
    description = "A simple script to perform Instant Runoff Voting base " \
        "on Google Form export csv file'"
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("input", nargs="?", default="ballots.csv", help="Input csv file")
    parser.add_argument("-o", "--output", dest="output", default="sankey_diagram.html")
    parser.add_argument("-s", "--show", dest="show", action="store_true", help="Show the sankey diagram in a new webpage")
    args = parser.parse_args()
    
    main(args)
