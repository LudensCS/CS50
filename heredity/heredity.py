import csv
import itertools
import sys
from typing import Dict, List

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def inherit(origin: int) -> float:
    """
    return the probability of inherit particular gene
    """
    if origin == 0:
        return PROBS["mutation"]
    elif origin == 1:
        return 0.5
    else:
        return 1 - PROBS["mutation"]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    conditions = {
        name: {
            "gene": 1 if name in one_gene else 2 if name in two_genes else 0,
            "trait": True if name in have_trait else False,
        }
        for name in people.keys()
    }
    deg: Dict[str, int] = dict.fromkeys(people, 0)
    G = {person: [] for person in people}
    q: List[str] = []
    for person in people:
        if people[person].get("mother"):
            deg[person] += 2
            G[people[person]["mother"]].append(person)
            G[people[person]["father"]].append(person)
    # toposort
    for person in deg:
        if deg[person] == 0:
            q.append(person)
    res: float = 1
    while len(q) > 0:
        u = q.pop()
        for v in G[u]:
            deg[v] -= 1
            if deg[v] == 0:
                q.append(v)
        res *= PROBS["trait"][conditions[u]["gene"]][conditions[u]["trait"]]
        if people[u].get("mother"):
            p1: float = inherit(conditions[people[u]["mother"]]["gene"])
            p2: float = inherit(conditions[people[u]["father"]]["gene"])
            if conditions[u]["gene"] == 0:
                res *= (1 - p1) * (1 - p2)
            elif conditions[u]["gene"] == 1:
                res *= (1 - p1) * p2 + p1 * (1 - p2)
            else:
                res *= p1 * p2
        else:
            res *= PROBS["gene"][conditions[u]["gene"]]
    return res
    # raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        probabilities[person]["trait"][(person in have_trait)] += p
        cnt: int = 1 if (person in one_gene) else 2 if (person in two_genes) else 0
        probabilities[person]["gene"][cnt] += p
    # raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for key1 in probabilities[person]:
            key_sum = sum(probabilities[person][key1].values())
            for key2 in probabilities[person][key1]:
                probabilities[person][key1][key2] /= key_sum
    # raise NotImplementedError


if __name__ == "__main__":
    main()
