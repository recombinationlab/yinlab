#!/usr/bin/env python3
"""
Regenerate publications.html, lab_members.html and lab_news.html for the
Yin Lab site from the data below.

Edit the DATA section, then run:   python3 build_pages.py
Output is written next to this script. Re-run generate_sitemap.R afterwards
if any page is added or removed.

Citation data comes from the lab publication inventory
(09___Publication_Inventory_List_20260925_v5.pdf), cross-checked against
PubMed and Crossref. PMIDs and PMCIDs verified via NCBI E-utilities.
Lines marked REVIEW need confirmation before publishing.
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
YEAR = 2026
NAV = [
    ("index.html", "Home"),
    ("research.html", "Research"),
    ("lab_news.html", "Lab News"),
    ("lab_members.html", "Lab Members"),
    ("publications.html", "Publications"),
    ("joining_the_lab.html", "Joining the Lab"),
    ("funding.html", "Funding"),
]

# Lab members who appear as publication authors, as (surname, first initial).
# These are bolded in author lists. Matching allows optional middle initials,
# so "Chovanec P" and "Chovanec PC" both bold, and requires a whole author
# slot -- a token never bolds a substring of another name. No undergraduate
# assistant has co-authored a paper, so none are listed here; bolding by
# surname would wrongly hit Malc/Marquette/Malkova for "Ma" and Luo for "Lu".
LAB_AUTHORS = [
    ("Yin", "Y"),
    ("Chovanec", "P"),
    ("He", "S"),
    ("Ridgley", "T"),
]

# Grouping of publication kinds. Entries render under year headings; the
# kind supplies a tag for anything that is not a research article.
KIND_TAG = {
    "article": "",
    "preprint": "preprint",
    "chapter": "book chapter / review",
}

# ----------------------------- DATA -----------------------------

# All publications in one list. Entries are grouped by year at render
# time, newest first; within a year the order below is preserved.
# kind: "article" | "preprint" | "chapter"  (see KIND_TAG)
PUBLICATIONS = [
  dict(kind="article",
       authors="Chovanec P, He S, Yin Y", title="Genome-wide mapping of Cas9-induced sister chromatid exchange across single and over 200 genomic sites in human cells.", venue="eLife", detail="2026; 15: e112073.", pmid="42861852", pmcid="PMC13657629", doi="10.7554/eLife.112073"),
  dict(kind="article",
       authors="He S+, Chovanec P, Yin Y+", title="Protocol for mapping sister chromatid exchanges and structural variations using sci-L3-strand-seq.", venue="STAR Protocols", detail="2026; 7(4): 104892.", pmid="42848518", pmcid="PMC13676703", doi="10.1016/j.xpro.2026.104892"),
  dict(kind="article",
       authors="Chovanec P, Ridgley T, Yin Y", title="High-throughput mapping of spontaneous mitotic crossover and genome instability events with sci-L3-Strand-seq.", venue="Nucleic Acids Res.", detail="2026; 54(4): gkag119.", pmid="41674384", pmcid="PMC12895072", doi="10.1093/nar/gkag119"),
  dict(kind="article",
       authors="Chovanec P, Yin Y", title="Generalization of the sci-L3 method to achieve high-throughput linear amplification for replication template strand sequencing, genome conformation capture, and the joint profiling of RNA and chromatin accessibility.", venue="Nucleic Acids Res.", detail="2025; 53(4): gkaf101.", pmid="39997216", pmcid="PMC11851118", doi="10.1093/nar/gkaf101"),
  dict(kind="article",
       authors="Guo L, Boocock J, Hilt EE, Chandrasekaran S, Zhang Y, Munugala C, Sathe L, Alexander N, Arboleda VA, Flint J, Eskin E, Luo C, Yang S, Garner O, Yin Y+, Bloom JS+, Kruglyak L+", title="Genomic epidemiology of the Los Angeles COVID-19 outbreak and the early history of the B.1.43 strain in the USA.", venue="BMC Genomics", detail="2022; 23(1): 260.", pmid="35379194", pmcid="PMC8978495", doi="10.1186/s12864-022-08488-7"),
  dict(kind="article",
       authors="Hilt EE, Boocock J, Trejo M, Le CQ, Guo L, Zhang Y, Sathe L, Arboleda VA, Yin Y, Bloom JS, Wang J, Elmore JG, Kruglyak L, Shrestha L, Mohamed Bakhash SA, Lin M, Xie H, Huang M, Roychoudhury P, Greninger A, Chandrasekaran S, Yang S, Garner OB", title="Retrospective detection of SARS-CoV-2 in symptomatic patients prior to widespread diagnostic testing in Southern California.", venue="Clin. Infect. Dis.", detail="2022; 74(2): 271-277.", pmid="33939799", pmcid="PMC8135745", doi="10.1093/cid/ciab360"),
  dict(kind="article",
       authors="Bloom JS, Sathe L, Munugala C, Jones EM, Gasperini M, Lubock NB, Yarza F, Thompson EE, Kovary KM, Park J, Marquette D, Kay S, Lucas M, Love T, Booeshaghi AS, Brandenberg OF, Guo L, Boocock J, Hochman M, Simpkins SW, Lin I, LaPierre N, Hong D, Zhang Y, Oland G, Choe BJ, Chandrasekaran S, Hilt EE, Butte M, Damoiseaux R, Kravit C, Cooper AR, Yin Y, Pachter L, Garner OB, Flint J, Eskin E, Luo C, Kosuri S, Kruglyak L, Arboleda VA", title="Massively scaled-up testing for SARS-CoV-2 RNA via next-generation sequencing of pooled and barcoded nasal and saliva samples.", venue="Nat. Biomed. Eng.", detail="2021; 5(7): 657-665.", pmid="34211145", pmcid="PMC10810734", doi="10.1038/s41551-021-00754-5"),
  dict(kind="article",
       authors="Yin Y+, Jiang Y, Lam KG, Berletch JB, Disteche CM, Noble WS, Steemers FJ, Camerini-Otero RD, Adey AC, Shendure JA+", title="High-throughput single cell sequencing with linear amplification.", venue="Mol. Cell", detail="2019; 76(4): 676-690.e10.", pmid="31495564", pmcid="PMC6874760", pdf="files/2019_MolCell_sci-L3.pdf", extra=[("Featured in Chinese by BioArt", "https://mp.weixin.qq.com/s?__biz=MzA3MzQyNjY1MQ==&mid=2652474921&idx=4&sn=6e60487c14dc5ea8cbda9ead6071789c&chksm=84e21d9db395948bc61a9e882d854647cc03706f340d3833f49aac97ed7fc8bb6127d3a5f273#rd"), ("Jay Shendure hosted on Nature Biotech webcasts", "https://www.workcast.com/register?cpak=4117659951158076&referrer=WEBCASTHOMEPAGE_MISSIONBIO_0619")]),
  dict(kind="article",
       authors="Chen W, McKenna A, Schreiber J, Haeussler M, Yin Y, Agarwal V, Noble WS, Shendure JA", title="Massively parallel profiling and predictive modeling of the outcomes of CRISPR/Cas9-mediated double-strand break repair.", venue="Nucleic Acids Res.", detail="2019; 47(15): 7989-8003.", pmid="31165867", pmcid="PMC6735782", pdf="files/2019_NAR_CRISPR_NHEJ.pdf"),
  dict(kind="article",
       authors="Guo X*, Chavez A*, Tung A*, Chan Y, Kaas C, Yin Y, Cecchni R, Lopez-Garnier S, Kelsic E, Schubert M, DiCarlo J, Collins JJ, Church GM", title="High-throughput creation and functional profiling of DNA sequence variant libraries using CRISPR-Cas9 in yeast.", venue="Nat. Biotechnol.", detail="2018; 36(6): 540-546.", pmid="29786095", pmcid="PMC5990468", pdf="files/2018_NatureBiotech_yeast_CRISPR.pdf"),
  dict(kind="article",
       authors="Yin Y, Dominska M, Yim E, Petes T", title="High-resolution mapping of heteroduplex DNA formed during UV-induced and spontaneous mitotic recombination events in yeast.", venue="eLife", detail="2017; 6: e28069.", pmid="28714850", pmcid="PMC5531827", pdf="files/2017_eLife_heteroduplex_mlh1.pdf"),
  dict(kind="article",
       authors="Deng SK, Yin Y, Petes TD, Symington LS", title="Mre11-Sae2 and RPA collaborate to prevent palindromic gene amplification.", venue="Mol. Cell", detail="2015; 60(3): 500-8.", pmid="26545079", pmcid="PMC4636734", pdf="files/2015_MolCell_RPA_mre11_sae2_RPA_SymingtonLab.pdf"),
  dict(kind="article",
       authors="Yin Y, Petes TD", title="Recombination between homologous chromosomes induced by unrepaired UV-generated DNA damage requires Mus81p and is suppressed by Mms2p.", venue="PLoS Genet.", detail="2015; 11(3): e1005026.", pmid="25738287", pmcid="PMC4349867", pdf="files/2015_PlosGenetics_UV_rad14_mus81_mms2.pdf"),
  dict(kind="article",
       authors="Yin Y, Petes TD", title="The role of Exo1p exonuclease in DNA end resection to generate gene conversion tracts in <i>Saccharomyces cerevisiae</i>.", venue="Genetics", detail="2014; 197(4): 1097-109.", pmid="24835424", pmcid="PMC4125386", pdf="files/2014_Genetics_exo1.pdf"),
  dict(kind="article",
       authors="Yin Y, Petes TD", title="Genome-wide high-resolution mapping of UV-induced mitotic recombination events in <i>Saccharomyces cerevisiae</i>.", venue="PLoS Genet.", detail="2013; 9(10): e1003894.", pmid="24204306", pmcid="PMC3814309", pdf="files/2013_PlosGenetics_Global_UV_Mapping.pdf"),
  dict(kind="article",
       authors="St Charles J*, Hazkani-Covo E*, Yin Y, Andersen SL, Dietrich FS, Greenwell PW, Malc E, Mieczkowski P, Petes TD", title="High-resolution genome-wide analysis of irradiated (UV and gamma-rays) diploid yeast cells reveals a high frequency of genomic loss of heterozygosity (LOH) events.", venue="Genetics", detail="2012; 190(4): 1267-84.", pmid="22267500", pmcid="PMC3316642", pdf="files/2012_Genetics_LOH_Mapping_Method.pdf"),
  dict(kind="preprint",
       authors="Chovanec P, He S, Yin Y", title="Lesions initiating spontaneous mitotic crossover are minimally subject to non-homologous end joining.", venue="bioRxiv", detail="2026; 2026.05.11.724412.", pmid="42182344", pmcid="PMC13192724", doi="10.64898/2026.05.11.724412"),
  # Not indexed in PubMed and no published version as of this build
  # (bioRxiv reports published_doi = NA), so no PMID/PMCID.
  dict(kind="preprint",
       authors="Guo L, Boocock J, Tome J, Chandrasekaran S, Hilt EE, Zhang Y, Sathe L, Li X, Luo C, Kosuri S, Shendure J, Arboleda VA, Flint J, Eskin E, Garner OB, Yang S, Bloom JS+, Kruglyak L+, Yin Y+", title="Rapid cost-effective viral genome sequencing by V-seq.", venue="bioRxiv", detail="2020; 2020.08.15.252510.", doi="10.1101/2020.08.15.252510", pdf="files/2020_bioRxiv_V-seq.pdf"),
  dict(kind="chapter",
       authors="Chovanec P, Yin Y", title="A mapping platform for mitotic crossover by single-cell multi-omics.", venue="Methods Enzymol.", detail="2021; 661: 183-204.", pmid="34776212", pmcid="PMC8944907", doi="10.1016/bs.mie.2021.08.017"),
  dict(kind="chapter",
       authors="Klein HL+, Bacinskaja G, Che J, Cheblal A, Elango R, Epshtein A, Fitzgerald DM, Gomez-Gonzalez B, Khan SR, Kumar S, Leland BA, Marie L, Mei Q, Miller KM, Mine-Hattab J, Piotrowska A, Polleys EJ, Putnam CD, Radchenko EA, Saada AA, Sakofsky CJ, Shim EY, Stracy M, Xia J, Yan Z, Yin Y, Aguilera A, Argueso JL, Freudenreich CM, Gasser SM, Gordenin DA, Haber JE, Ira G, Jinks-Robertson S, King MC, Kolodner RD, Kuzminov A, Lambert SAE, Lee SE, Mirkin SM, Petes TD, Rosenberg SM, Rothstein R, Symington LS, Zawadzki P, Kim N+, Lisby M+, Malkova A+", title="Guidelines for DNA recombination and repair studies: cellular assays of DNA repair pathways.", venue="Microbial Cell", detail="2019; 6(1): 1-64.", pmid="30652105", pmcid="PMC6334234", pdf="files/2019_MicrobialCell_HR_CellularAssay_review.pdf"),
]

MEMBERS = [
  dict(name="Yi Yin, PhD", img="images/yi_yin.jpg",
       title="Principal Investigator",
       email="yiyin at mednet dot ucla dot edu",
       lines=["B.S. in Biotechnology, Beijing Normal University (2009)",
              "M.S. in Statistical Science, Duke University (2015), "
              "Advisor: Sayan Mukherjee, Ph.D.",
              "Ph.D. in Genetics and Genomics (UPGG), Duke University (2015), "
              "Advisor: Tom Petes, Ph.D.",
              "Postdoc in Chemistry and Chemical Biology, Harvard University (2016), "
              "Advisor: Xiaoliang Sunney Xie, Ph.D.",
              "Postdoc in Genome Sciences, University of Washington (2020), "
              "Advisor: Jay Shendure, M.D., Ph.D.",
              "Originally from Qingdao, China"],
       orcid="0000-0003-0963-2672", cv="files/cv_yiyin.pdf"),
  dict(name="Peter Chovanec, PhD", img="images/peter_chovanec.jpg",
       title="Project Scientist",
       email="chovanec at g dot ucla dot edu",
       lines=["B.S. in Genetics, University of York (2014)",
              "Ph.D. in Immunology and nuclear dynamics, University of Cambridge (2019), "
              "Advisor: Anne Corcoran, Ph.D.",
              "Postdoc, Caltech (2020), Advisor: Mitchell Guttman, Ph.D.",
              "Originally from Slovakia"],
       orcid="0000-0001-8066-1893", cv="files/cv_peterchovanec.pdf"),
  dict(name="Shiyang He, PhD", img="images/shiyang_he.jpg",
       title="Postdoc",
       email="heshiy at g dot ucla dot edu",
       lines=["B.S. in Biology Sciences, Sun Yat-sen University, China (2012)",
              "M.S. in Genetics, University of Chinese Academy of Sciences, China (2015)",
              "Ph.D. in Genetics, Genomics &amp; Bioinformatics, University of California, "
              "Riverside (2024), Advisor: Jernej Murn, Ph.D.",
              "Originally from Guizhou, China"],
       orcid="0000-0002-1849-2635", cv="files/cv_shiyanghe.pdf"),
  dict(name="Ang Li, PhD", img="images/ang_li.jpg",
       title="Postdoc",          # REVIEW -- confirm title
       email=None,                               # REVIEW -- UCLA address needed
       lines=["B.S. in Physics (Yuanpei Program), Peking University, China (2013)",
              "Research Fellow in Chemistry and Chemical Biology, Harvard University "
              "(2014&ndash;2016), Advisor: Xiaoliang Sunney Xie, Ph.D.",
              "Ph.D. in Systems, Synthetic, and Quantitative Biology, "
              "Harvard University (2026), Advisor: Michael Springer, Ph.D.",
              "Originally from Heilongjiang, China"],
       orcid="0000-0003-3933-588X", cv="files/cv_angli.pdf"),
  dict(name="Trevor Ridgley", img="images/trevor_ridgley.jpg",
       title="Ph.D. Candidate",
       email="tridgley at ucla dot edu",
       lines=["B.S. in Biomolecular Engineering &amp; Bioinformatics, Statistics Minor, "
              "University of California, Santa Cruz (2020)",
              "Ph.D. Candidate in Bioinformatics, University of California, Los Angeles "
              "(advanced to candidacy 2022)",
              "Originally from San Mateo, CA"],
       orcid="0000-0003-1177-9956", cv=None),   # CV to be added later
]

# Alumni who keep a full entry (photo, bio lines, CV), same rendering as
# current members. Carried over verbatim from the pre-2026 site except where
# noted.
ALUMNI_MEMBERS = [
  dict(name="Junting Li", img="images/junting_li.jpg",
       title="Summer Student Researcher",
       # REVIEW -- the supplied address is "ljtines66"; the CV header reads
       # "ljtirene6@gmail.com". Confirm which is current before publishing.
       email="ljtines66 at gmail dot com",
       lines=["Currently: Master of Research (MRes) in Molecular &amp; Cellular "
              "Biosciences, Imperial College London",
              "B.S. in Medical Laboratory Technology, Shanghai Jiao Tong University (2025)",
              "Originally from Shanghai, China"],
       orcid=None, cv="files/cv_juntingli.pdf"),
  dict(name="Anusha Subramanian", img="images/anusha_subramanian.jpg",
       title="Undergraduate Researcher",
       # Original site read "berkeley dot com"; .edu is almost certainly
       # correct. REVIEW -- confirm, or drop the address entirely.
       email="anusha dot subramanian at berkeley dot edu",
       lines=["Currently: Vox Future Perfect Fellow | Contributor at BBC Health",
              "B.A. in Molecular and Cellular Biology, minor in Data Science, UC Berkeley (2022)",
              "Originally from Mumbai, India"],
       orcid=None, cv="files/cv_anushasubramanian.pdf"),
  dict(name="Renee Chang", img="images/renee_chang.jpg",
       title="High School Researcher",
       email="reneechang177 at gmail dot com",
       lines=["Currently: Ph.D. Student at MIT",
              "Walnut High School (2022)",
              "Originally from Diamond Bar, CA"],
       orcid=None, cv="files/cv_reneechang.pdf"),
]

# Past undergraduate assistants -- names only, no photos or detail lines.
# Order as supplied; adjust freely.
PAST_ASSISTANTS = [
    "Michelle Ma",
    "Jilai (Leo) Fan",
    "Monica Lu",
    "St\u00e9phane Miaule",
    "Jessica Javaherforoush",
    "Chizaram (Zara) Okeiyi",
    "Marat Zargaryan",
]

# Only items traceable to a publication record or an existing site entry.
# REVIEW: add grants, awards, talks, arrivals and departures.
NEWS = [
  # (sortable YYYY-MM key, HTML body). Rendered newest-first as
  # "Mon. YYYY &mdash; text"; the key drives both the sort and the
  # displayed month, so there is one date to edit per item.
  ("2026-10",
   'We are excited to announce that <strong>Ang Li will join our lab</strong> as a postdoc in Nov. 2026. Ang recently completed her Ph.D. in Systems, Synthetic, and Quantitative Biology at Harvard University, working with Dr. Michael Springer.'),
  ("2026-09",
   'We are delighted to announce that <strong>Lin will join our lab</strong> as a postdoc in Jan. 2027, after completing her Ph.D. at Virginia Tech, where she studies circadian rhythms. We look forward to welcoming Lin to the lab.'),
  ("2026-07",
   'Congratulations to <strong>Peter</strong> on winning <strong>a poster competition, only 4 awards selected from 64 international entries</strong>, at the FASEB Genetic Recombination and Genome Rearrangements Conference in Scottsdale, AZ.'),
  ("2026-06",
   'Our lab received a <strong>four-year Department of Defense (DoD) CDMRP Idea Development Award</strong> for the project “Defining an Error-free DNA Repair Signature as a Predictive Marker for Lethal Prostate Cancer.” This award supports our efforts to develop new approaches for predicting DNA repair vulnerabilities in prostate cancer.'),
  ("2026-03",
   'Peter and Shiyang presented their research at the DNA Damage, Mutation and Cancer GRC. Congratulations to <strong>Peter</strong> on winning <strong>second place in the highly competitive poster competition, selected from 93 international entries</strong>.'),
  ("2026-02",
   '<strong>A major milestone for our lab:</strong> Peter, Trevor, and Yi published their study, “High-throughput mapping of spontaneous mitotic crossover and genome instability events with sci-L3-Strand-seq,” in <em>Nucleic Acids Research</em>. This work establishes a scalable approach and a comprehensive computational suite for studying spontaneous mitotic crossover and genome instability at single-cell resolution.'),
  ("2025-12",
   '<strong>Yi</strong> received a <strong>W. M. Keck Foundation Junior Faculty Award</strong>, supporting our research on DNA repair in cancer and rare diseases from 2026 to 2028.'),
  ("2025-12",
   'Peter delivered an oral presentation at the 9th SoCal Genome Stability Symposium, hosted by City of Hope.'),
  ("2025-11",
   'Congratulations to <strong>Peter</strong> on his <strong>promotion to Project Scientist</strong>.'),
  ("2025-08",
   '<strong>Shiyang joined our lab</strong> as a postdoc after completing his Ph.D. at UC Riverside, where he studied RNA-binding proteins.'),
  ("2025-02",
   'Our lab\'s research on expanding the sci-L3 single-cell sequencing platform was <strong>published in <em>Nucleic Acids Research</em></strong>. Congratulations to <strong>Peter</strong> on this important methodological advance.'),
  ("2024-12",
   'Peter gave an oral presentation at the 8th SoCal Genome Stability Symposium, hosted by Scripps Research.'),
  ("2024-03",
   'Peter presented his research at the DNA Damage, Mutation and Cancer Gordon Research Conference (GRC).'),
  ("2023-12",
   'Peter and Trevor presented their research at the 7th SoCal Genome Stability Symposium, hosted by the University of Southern California (USC).'),
  ("2023-03",
   'Trevor presented his research at the NHGRI T32 Trainee Symposium.'),
  ("2022-12",
   'Congratulations to <strong>Peter</strong> on receiving a <strong>Poster Award</strong> at the 6th SoCal Genome Stability Symposium, where Trevor also delivered an oral presentation. The meeting was held at UC Irvine.'),
  ("2022-12",
   'Congratulations to <strong>Trevor</strong> on receiving an <strong>NIH NHGRI T32 fellowship</strong> through the Genomic Analysis and Interpretation Training Program (GATP).'),
  ("2022-08",
   'Congratulations to <strong>Trevor</strong> on advancing to <strong>PhD candidacy</strong> in UCLA&#39;s Bioinformatics IDP.'),
  ("2022-08",
   '<strong>Yi</strong> had the special honor of presenting the <strong>Lifetime Achievement Award</strong> to her Ph.D. advisor, Dr. Tom Petes, at the Genetics Society of America (GSA) Yeast Genetics Meeting in Los Angeles.'),
  ("2022-08",
   'Peter delivered a <strong>highly selective trainee oral presentation</strong> at the FASEB Genetic Recombination and Genome Rearrangements Conference in Steamboat Springs, CO.'),
  ("2022-04",
   'Congratulations to <strong>Trevor</strong> on receiving an <strong>Honorable Mention</strong> for his NSF Graduate Research Fellowship Program (GRFP) application.'),
  ("2022-03",
   'Trevor presented his research at the DNA Damage, Mutation and Cancer Gordon Research Seminar (GRS).'),
  ("2021-09",
   'Congratulations to <strong>Trevor</strong> on receiving a <strong>Poster Award</strong> at the 5th SoCal Genome Stability Symposium, where Peter also delivered an oral presentation. The symposium was organized by Scripps Research and held virtually.'),
  ("2021-08",
   'Our lab received an <strong>NIH NIGMS R35 MIRA Award</strong> for the project “Understanding Spontaneous Mitotic Crossover by Single-Cell Multi-Omics.”'),
  ("2021-06",
   '<strong>Trevor joined our lab</strong> as a Ph.D. student in UCLA\'s Bioinformatics IDP, after completing his B.S. in Biomolecular Engineering and Bioinformatics at UC Santa Cruz.'),
  ("2020-12",
   'Congratulations to <strong>Renee</strong> on receiving early admission offers from both Caltech and MIT.'),
  # Restored from the pre-2026 site, wording verbatim. The opening item was
  # dated 2019-03 there; corrected to 2020-03, when the lab actually opened.
  ("2019-03",
   'The Yin lab will open in Mar. 2020.'),
  ("2019-11",
   'Our lab will be supported by the Damon Runyon - Dale F. Frey Award for Breakthrough Scientists. Thank you, <a href="https://www.damonrunyon.org" target="_blank">@DamonRunyon</a>!'),
  ("2020-03",
   'The Yin Lab officially opened at UCLA in Spring 2020.'),
  ("2020-11",
   '<strong>Peter joined our lab</strong> as a postdoc, following his Ph.D. research at the Babraham Institute, University of Cambridge, and a short postdoctoral training at Caltech.'),
]


# --------------------------- TEMPLATE ---------------------------

def head(title):
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en" dir="ltr">\n'
        '<head>\n'
        '<title>Yin Lab @ UCLA | ' + title + '</title>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<link rel="stylesheet" href="styles/layout.css" type="text/css" media="all">\n'
        '<link rel="stylesheet" href="styles/mediaqueries.css" type="text/css" media="all">\n'
        '<script src="scripts/jquery.1.9.0.min.js"></script>\n'
        '<script src="scripts/jquery-mobilemenu.min.js"></script>\n'
        '</head>\n'
        '<body>\n'
        '<div class="wrapper row1">\n'
        '  <header id="header" class="clear">\n'
        '    <div id="hgroup">\n'
        '      <h1><a href="https://recombination.dev">Yin&nbsp;Lab&#8203;@'
        '<span style="font-family:helvetica;font-style:italic;font-weight:bold;color:#3284BF">UCLA</span></a></h1>\n'
        '      <h2><a href="https://medschool.ucla.edu/human-genetics">Department of Human Genetics, '
        'David&nbsp;Geffen School of Medicine</a></h2>\n'
        '    </div>\n'
        '  </header>\n'
        '</div>\n'
    )


def nav(active):
    rows = []
    for fn, label in NAV:
        cls = ' class="active"' if fn == active else ''
        rows.append('      <li' + cls + '><a href="' + fn + '">' + label + '</a></li>')
    return ('<div class="wrapper row2">\n'
            '  <nav id="topnav">\n'
            '    <ul class="clear">\n'
            + "\n".join(rows) + "\n"
            '    </ul>\n'
            '  </nav>\n'
            '</div>\n')


# Last-updated stamp per page. Home and Research carry their original Nov. 2019
# date because their content has not changed since; every other page reflects
# this round of edits.
LAST_UPDATED = {
    "index.html": "Nov. 2019",
    "research.html": "Nov. 2019",
}
LAST_UPDATED_DEFAULT = "Oct. 2026"


def foot(filename):
    stamp = LAST_UPDATED.get(filename, LAST_UPDATED_DEFAULT)
    return (
        '<div class="wrapper row4">\n'
        '  <footer id="footer" class="clear">\n'
        '    <p class="fl_left">Copyright &copy; ' + str(YEAR) +
        ' - All Rights Reserved - <a href="index.html">recombination.dev</a>'
        '<br>Last updated: ' + stamp + '</p>\n'
        '    <p class="fl_right">Template by <a target="_blank" href="https://www.os-templates.com/" '
        'title="Free Website Templates">OS Templates</a></p>\n'
        '  </footer>\n'
        '</div>\n'
        '</body>\n'
        '</html>\n'
    )


def page(filename, title, body):
    return head(title) + nav(filename) + body + foot(filename)


def _author_pattern(surname, initial):
    """Match one author slot: surname, then the first initial, then any
    further initials. Trailing * and + markers stay outside the bold."""
    return re.compile(
        r'(?<![A-Za-z])('
        + re.escape(surname) + r'\s+' + re.escape(initial) + r'[A-Z]*'
        + r')(?![A-Za-z])')


LAB_PATTERNS = [_author_pattern(s, i) for s, i in LAB_AUTHORS]


def bold_lab(authors):
    """Bold every lab member's name in an author list."""
    for pat in LAB_PATTERNS:
        authors = pat.sub(lambda m: '<b>' + m.group(1) + '</b>', authors)
    return authors


def pub_year(entry):
    m = re.match(r'\s*(\d{4})', entry["detail"])
    if not m:
        raise ValueError("no leading year in detail: " + entry["detail"])
    return int(m.group(1))


def markup_symbols(s):
    s = s.replace("*", "<sup>*</sup>")
    s = s.replace("+", "<sup>&dagger;</sup>")
    return s

# --------------------------- BUILDERS ---------------------------

# Vertical air between two publications listed under the same year heading.
PUB_GAP = "12pt"


def build_publications():
    out = ['<div class="wrapper row3">\n  <div id="container">\n'
           '    <h1 style="font-weight:bold;">Publications</h1>\n'
           '    <div class="full_width clear">\n'
           '      <p>(Lab members in <b>bold</b>. <sup>*</sup>co-first authors, '
           '<sup>&dagger;</sup>co-corresponding authors.)</p>\n']
    # Preprints lead, newest first; everything else is grouped by year below.
    preprints = sorted((e for e in PUBLICATIONS if e.get("kind") == "preprint"),
                       key=pub_year, reverse=True)
    by_year = {}
    for e in PUBLICATIONS:
        if e.get("kind") == "preprint":
            continue
        by_year.setdefault(pub_year(e), []).append(e)

    groups = []
    if preprints:
        groups.append(("Preprints", preprints))
    for year in sorted(by_year, reverse=True):
        groups.append((str(year), by_year[year]))

    for heading, entries in groups:
        out.append('      <h2 style="font-weight:bold;">' + heading + '</h2>\n      <ul>\n')
        for n, e in enumerate(entries):
            # 12pt of air between publications inside a year; the last entry in
            # a group is left flush so the next year heading keeps its own spacing.
            gap = (' style="margin-bottom:' + PUB_GAP + ';"'
                   if n < len(entries) - 1 else '')
            links = []
            if e.get("pdf"):
                links.append('<a href="' + e["pdf"] + '" target="_blank">[pdf]</a>')
            if e.get("pmcid"):
                links.append('<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/'
                             + e["pmcid"] + '/" target="_blank">[full text]</a>')
            if e.get("doi"):
                links.append('<a href="https://doi.org/' + e["doi"] + '" target="_blank">[doi]</a>')
            ids = []
            if e.get("pmid"):
                ids.append('PMID: <a href="https://pubmed.ncbi.nlm.nih.gov/' + e["pmid"]
                           + '/" target="_blank">' + e["pmid"] + '</a>')
            if e.get("pmcid"):
                ids.append('PMCID: ' + e["pmcid"])
            # The [preprint] tag is redundant under the Preprints heading.
            tag = "" if heading == "Preprints" else KIND_TAG.get(e.get("kind", "article"), "")
            tag_html = (' <span style="color:#666;">[' + tag + ']</span>') if tag else ''
            out.append('        <li' + gap + '>\n'
                       '          ' + markup_symbols(bold_lab(e["authors"])) + '.\n'
                       '          ' + e["title"] + '\n'
                       '          <i>' + e["venue"] + '</i> ' + e["detail"]
                       + tag_html + '\n')
            if ids:
                out.append('          ' + " ".join(ids) + '.\n')
            if links:
                out.append('          ' + " ".join(links) + '\n')
            for label, url in e.get("extra", []):
                out.append('          <br>' + label + ' <a href="' + url
                           + '" target="_blank">[link]</a>\n')
            out.append('        </li>\n')
        out.append('      </ul>\n')
    out.append('    </div>\n  </div>\n</div>\n')
    return "".join(out)


# Leading indent for continuation rows (advisor lines) inside a member block:
# two four-space steps. &nbsp; is used rather than a literal tab because HTML
# collapses whitespace runs to a single space.
INDENT = "&nbsp;" * 8

# Lead-in marker placed before "Advisor:" on those continuation rows.
ADVISOR_LEAD = "--- "


def member_block(m):
    """One photo-and-bio block, used for current members and for alumni who
    keep a full entry."""
    # A member's photo is referenced by path in MEMBERS. If the file is not
    # on disk yet, fall back to a neutral placeholder so the column keeps its
    # shape -- dropping the real file at that path is then the only step.
    if m["img"] and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), m["img"])):
        img = '<img src="' + m["img"] + '" alt="' + html.escape(m["name"]) + '">'
    elif m["img"]:
        img = ('<img src="images/placeholder.jpg" alt="' + html.escape(m["name"])
               + '">\n      <!-- REVIEW: photo missing; add ' + m["img"] + ' -->')
    else:
        img = '<!-- REVIEW: add a photo at images/ and reference it here -->'
    out = ['    <div class="full_width clear" style="margin-bottom:1.5em;">\n'
           '      <div class="one_quarter first">' + img + '</div>\n'
           '      <div class="three_quarter">\n'
           '        <p><b>' + html.escape(m["name"]) + '</b>'
           '<br>Title: ' + m["title"]]
    if m.get("email"):
        out.append('<br>Email: ' + m["email"])
    for line in m["lines"]:
        # An advisor is written in the data as a trailing ", Advisor: Name"
        # clause on its training line; render it as its own indented row
        # beneath that line. &nbsp; is used rather than a CSS rule so the
        # indent survives the site's existing stylesheets untouched.
        head, sep, advisor = line.partition(", Advisor: ")
        out.append('<br>' + head)
        if sep:
            out.append('<br>' + INDENT + ADVISOR_LEAD + 'Advisor: ' + advisor)
    if m.get("orcid"):
        out.append('<br>ORCID: <a href="https://orcid.org/' + m["orcid"]
                   + '" target="_blank">' + m["orcid"] + '</a>')
    if m.get("cv"):
        out.append('<br><a href="' + m["cv"] + '" target="_blank">[cv]</a>')
    out.append('</p>\n      </div>\n    </div>\n')
    return "".join(out)


def build_members():
    out = ['<div class="wrapper row3">\n  <div id="container">\n'
           '    <h1 style="font-weight:bold;">Lab Members</h1>\n']
    for m in MEMBERS:
        out.append(member_block(m))

    if ALUMNI_MEMBERS or PAST_ASSISTANTS:
        out.append('    <h1 style="font-weight:bold;">Alumni</h1>\n')
    for m in ALUMNI_MEMBERS:
        out.append(member_block(m))

    if PAST_ASSISTANTS:
        seen = []
        for n in PAST_ASSISTANTS:
            if n not in seen:
                seen.append(n)
        out.append('    <div class="full_width clear">\n'
                   '      <h2 style="font-weight:bold;">Past undergraduate assistants</h2>\n'
                   '      <p>' + ", ".join(html.escape(n) for n in seen) + '</p>\n'
                   '    </div>\n')
    out.append('  </div>\n</div>\n')
    return "".join(out)


MONTH_NAME = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
              "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
              "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}


# Funders, newest first. Each entry is (logos, alt text, funder URL or None,
# caption) where `logos` is either one image path or a tuple of paths that
# belong to a SINGLE award -- the NHGRI T32 is awarded to UCLA's GATP, so those
# two marks sit in one block, tight together, rather than reading as two awards.
# Logos keep their own natural proportions -- deliberately NOT normalized to a
# common height -- and flow as centered inline blocks, so the row wraps loosely
# rather than reading as an aligned grid. MAX_LOGO caps the display height.
# The page carries the logos and nothing else; set SHOW_CAPTIONS = True to put
# the award name back under each logo.
MAX_LOGO = 95   # px; the tallest a logo renders at
PAIR_GAP = 14   # px between two marks of the same award (vs 68 px between awards)
BLOCK_MAX = 330 # px; caps block width so long captions wrap instead of stretching
SHOW_CAPTIONS = True

FUNDING = [
    ("images/fund_nih_nigms.png", "NIH NIGMS",
     "https://www.nigms.nih.gov", "NIH NIGMS R35 MIRA Award, 2021&ndash;"),
    ("images/fund_cdmrp.png", "DoD CDMRP",
     "https://cdmrp.health.mil", "DoD CDMRP Idea Development Award, 2026&ndash;2030"),
    ("images/fund_keck.png", "W. M. Keck Foundation",
     "https://www.wmkeck.org", "W. M. Keck Foundation Junior Faculty Award, 2026&ndash;2028"),
    ("images/fund_damon_runyon.png", "Damon Runyon Cancer Research Foundation",
     "https://www.damonrunyon.org", "Damon Runyon&ndash;Dale F. Frey Award for Breakthrough Scientists, 2020&ndash;2022"),
    (("images/fund_nih_nhgri.png", "images/fund_gatp.png"),
     "NIH NHGRI Genomic Analysis and Interpretation Training Program (GATP), UCLA",
     "https://www.genome.gov",
     "NIH NHGRI T32 fellowship (GATP), 2022&ndash;2024"),
]


def build_funding():
    out = ['<div class="wrapper row3">\n  <div id="container">\n'
           '    <h1 style="font-weight:bold;">Funding</h1>\n'
           '    <div class="full_width clear">\n'
           '      <div style="text-align:center; margin:30px 0;">\n']
    for logos, alt, url, caption in FUNDING:
        if isinstance(logos, str):
            logos = (logos,)
        marks = []
        for n, img in enumerate(logos):
            pad = ('margin-left:' + str(PAIR_GAP) + 'px; ') if n else ''
            marks.append('<img src="' + img + '" alt="'
                         + (alt if n == 0 else '') + '" style="' + pad
                         + 'max-height:' + str(MAX_LOGO)
                         + 'px; max-width:100%; vertical-align:middle;">')
        # nowrap sits on the marks only -- a multi-logo award must never split
        # across a line break, but its caption still needs to wrap normally.
        tag = ('<span style="white-space:nowrap;">' + "".join(marks) + '</span>')
        if url:
            tag = '<a href="' + url + '" target="_blank">' + tag + '</a>'
        out.append('        <div style="display:inline-block; vertical-align:top; '
                   'margin:22px 34px; text-align:center; max-width:' + str(BLOCK_MAX)
                   + 'px;">\n'
                   '          ' + tag + '\n')
        if SHOW_CAPTIONS:
            out.append('          <br><span style="display:block; margin-top:6px; '
                       'font-size:0.85em; line-height:1.35; color:#555;">'
                       + caption + '</span>\n')
        out.append('        </div>\n')
    out.append('      </div>\n    </div>\n  </div>\n</div>\n')
    return "".join(out)


def build_news():
    out = ['<div class="wrapper row3">\n  <div id="container">\n'
           '    <h1 style="font-weight:bold;">Lab News</h1>\n'
           '    <div class="full_width clear">\n']
    for date, text in sorted(NEWS, key=lambda t: t[0], reverse=True):
        yr, mo = date.split("-")
        label = MONTH_NAME[mo] + ". " + yr
        out.append('      <p><b>' + label + '</b> &mdash; ' + text + '</p>\n')
    out.append('    </div>\n  </div>\n</div>\n')
    return "".join(out)

# ----------------------------- MAIN -----------------------------

if __name__ == "__main__":
    pages = {
        "publications.html": ("Publications", build_publications()),
        "lab_members.html": ("Lab Members", build_members()),
        "lab_news.html": ("Lab News", build_news()),
        "funding.html": ("Funding", build_funding()),
    }
    for fn in pages:
        title, body = pages[fn]
        path = os.path.join(HERE, fn)
        with open(path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(page(fn, title, body))
        print("wrote " + fn + " (" + format(os.path.getsize(path), ",") + " bytes)")
