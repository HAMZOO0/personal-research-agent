import json
import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def pubmed_search_tool(query: str, max_results: int = 5) -> str:
    """Search PubMed for peer-reviewed medical/biomedical research papers."""
    try:
        # Step 1: Search for PMIDs
        search_resp = requests.get(
            f"{EUTILS}/esearch.fcgi",
            params={
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance",
            },
            headers={"User-Agent": "ResearchAssistant/1.0"},
            timeout=15,
        )
        search_resp.raise_for_status()
        id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return f"No PubMed papers found for query: {query}"

        # Step 2: Fetch summaries for all PMIDs in one request
        summary_resp = requests.get(
            f"{EUTILS}/esummary.fcgi",
            params={
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
            },
            headers={"User-Agent": "ResearchAssistant/1.0"},
            timeout=15,
        )
        summary_resp.raise_for_status()
        summary_data = summary_resp.json().get("result", {})

        # Step 3: Fetch abstracts in bulk
        abstract_resp = requests.get(
            f"{EUTILS}/efetch.fcgi",
            params={
                "db": "pubmed",
                "id": ",".join(id_list),
                "rettype": "abstract",
                "retmode": "text",
            },
            headers={"User-Agent": "ResearchAssistant/1.0"},
            timeout=20,
        )
        abstract_resp.raise_for_status()
        # Split raw abstract text by PMID markers
        raw_abstracts = abstract_resp.text

        results = []
        for pmid in id_list:
            doc = summary_data.get(pmid, {})
            if not doc:
                continue

            title = doc.get("title", "Unknown Title").rstrip(".")
            authors_raw = doc.get("authors", [])
            authors = ", ".join(
                a.get("name", "") for a in authors_raw[:5]
            ) + (" et al." if len(authors_raw) > 5 else "")
            pub_date = doc.get("pubdate", "Unknown Date")
            source = doc.get("source", "")  # journal name

            # Extract abstract snippet for this PMID from the bulk text
            abstract_snippet = ""
            marker = f"PMID: {pmid}"
            if marker in raw_abstracts:
                idx = raw_abstracts.index(marker)
                chunk = raw_abstracts[max(0, idx - 2000):idx + 100]
                lines = [l.strip() for l in chunk.splitlines() if l.strip()]
                # Take up to 6 lines before the PMID line as the abstract
                abstract_snippet = " ".join(lines[-7:-1])[:600]

            results.append(
                f"PMID: {pmid}\n"
                f"Title: {title}\n"
                f"Authors: {authors}\n"
                f"Journal: {source}\n"
                f"Published: {pub_date}\n"
                f"Abstract: {abstract_snippet or '(See full paper for abstract)'}\n"
                f"URL: https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n"
                f"Full Text: https://www.ncbi.nlm.nih.gov/pmc/articles/?term={pmid}"
            )

        return "\n\n" + ("-" * 60 + "\n\n").join(results)

    except Exception as e:
        return f"Error searching PubMed: {str(e)}"
