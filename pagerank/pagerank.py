import os
import random
import re
import sys
from typing import Dict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor) -> Dict[str,float]:
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    if len(corpus[page])==0:
        return dict.fromkeys(corpus,1/len(corpus))
    res:Dict[str,float] = dict.fromkeys(corpus,(1-float(damping_factor))/len(corpus))
    for val in corpus[page]:
        res[val] += damping_factor/len(corpus[page])
    return res
    # raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    res = dict.fromkeys(corpus,0)
    page = random.choice(list(corpus.keys()))
    res[page] += 1
    for _ in range(n-1):
        prob:Dict[str,float] = transition_model(corpus,page,damping_factor)
        seed:float = random.uniform(0,1)
        for nxtpage,val in prob.items():
            seed -= val
            if seed <= 0:
                page=nxtpage
                break
        res[page] += 1
    for key in res:
        res[key] /= n
    return res
    # raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    res:Dict[str,float] = dict.fromkeys(corpus,1/len(corpus))
    EPS = 1e-3
    converge = False
    while not converge:
        converge = True
        newRes:Dict[str,float] = dict.fromkeys(corpus,(1-float(damping_factor))/len(corpus))
        for u in newRes:
            for v in newRes:
                if len(corpus[v]) == 0:
                    newRes[u] += damping_factor*res[v]/len(corpus)
                elif u in corpus[v]:
                    newRes[u] += damping_factor*res[v]/len(corpus[v])
        for u in res:
            if abs(res[u] - newRes[u])>EPS:
                converge = False
                break
        res=newRes
    return res
    # raise NotImplementedError


if __name__ == "__main__":
    main()
