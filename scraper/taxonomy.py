"""
Event Horizon 2.0 taxonomy: everything that decides *what an event is about*.

How much an event matters is NOT decided here: that is a property of a research
profile (scraper/profiles.yaml), so the same tagged events can be ranked
differently for different researchers.

Structure
---------
FIELDS      top-level fields, in display order
SUBFIELDS   sub-field id -> (parent field, label)
RULES       sub-field id -> list of regex patterns (word-boundary safe)
DECLARED    subject codes that *organisers* attach to events (arXiv-style
            researchseminars topics, INSPIRE categories, ai-deadlines tags)
            -> sub-fields. Declared codes are the most trustworthy evidence.
PROTOTYPES  one-paragraph descriptions of each sub-field, used by the
            embedding classifier (Option B) to catch events with no keywords.
"""

import re

# ---------------------------------------------------------------------------
# Fields and sub-fields
# ---------------------------------------------------------------------------
FIELDS = {
    "cosmo":   "Cosmology",
    "astro":   "Astrophysics",
    "ai":      "AI / ML",
    "cs":      "Computer science",
    "math":    "Mathematics",
    "physics": "Physics",
}

# id: (parent field, label). Display order follows this table.
SUBFIELDS = {
    "cosmo.de":      ("cosmo", "Dark energy & expansion"),
    "cosmo.lss":     ("cosmo", "Large-scale structure & surveys"),
    "cosmo.early":   ("cosmo", "CMB & early universe"),
    "cosmo.dm":      ("cosmo", "Dark matter"),
    "cosmo.general": ("cosmo", "Cosmology (general)"),

    "ai.science":    ("ai", "ML for science"),
    "ai.theory":     ("ai", "ML theory & optimisation"),
    "ai.genai":      ("ai", "Generative models & LLMs"),
    "ai.nlp":        ("ai", "Language & speech"),
    "ai.vision":     ("ai", "Computer vision & multimodal"),
    "ai.rl":         ("ai", "Reinforcement learning & agents"),
    "ai.trust":      ("ai", "Safety, fairness & interpretability"),
    "ai.general":    ("ai", "AI / ML (general)"),

    "cs.theory":     ("cs", "Algorithms & theory of computation"),
    "cs.systems":    ("cs", "Systems, networks & HPC"),
    "cs.security":   ("cs", "Security & cryptography"),
    "cs.pl":         ("cs", "Programming languages & software"),
    "cs.data":       ("cs", "Databases, data mining & retrieval"),
    "cs.hci":        ("cs", "HCI, graphics & visualisation"),
    "cs.robotics":   ("cs", "Robotics"),
    "cs.general":    ("cs", "Computer science (other)"),

    "astro.he":       ("astro", "High-energy, compact objects & GW"),
    "astro.galactic": ("astro", "Galaxies & AGN"),
    "astro.stellar":  ("astro", "Stars, Sun & planets"),
    "astro.general":  ("astro", "Astronomy (general)"),

    "math.nt":        ("math", "Number theory"),
    "math.topology":  ("math", "Topology"),
    "math.algebra":   ("math", "Algebra & representation theory"),
    "math.geometry":  ("math", "Geometry"),
    "math.probability": ("math", "Probability & statistics"),
    "math.mathphys":  ("math", "Mathematical physics"),
    "math.analysis":  ("math", "Analysis & PDE"),
    "math.other":     ("math", "Other mathematics"),

    "phys.gr":       ("physics", "Gravitation & GR"),
    "phys.hepth":    ("physics", "High-energy theory & QFT"),
    "phys.quantum":  ("physics", "Quantum physics"),
    "phys.condmat":  ("physics", "Condensed matter & stat mech"),
    "phys.fluids":   ("physics", "Fluids, plasma & climate"),
    "phys.general":  ("physics", "Physics (other)"),
}


# ---------------------------------------------------------------------------
# Keyword rules. All patterns are case-insensitive and word-bounded unless the
# pattern says otherwise. Patterns starting with "CS:" are case-sensitive
# (for acronyms like AI, SBI, DESI that collide with ordinary words).
# ---------------------------------------------------------------------------
W = r"\b"
RULES = {
    "cosmo.general": [
        r"cosmolog\w*", r"cosmic (?:web|expansion|history|structure)",
        r"big bang", r"lambda-?cdm", r"CS:ΛCDM", r"CS:LCDM", r"friedmann",
        r"CS:FLRW", r"standard model of cosmology", r"primordial universe",
    ],
    "cosmo.de": [
        r"dark energy", r"cosmic acceleration", r"accelerat\w* expansion",
        r"hubble (?:tension|constant|parameter)", r"CS:H_?0 tension",
        r"expansion history", r"quintessence", r"phantom (?:crossing|dark|divide|regime)",
        r"CS:w0-?wa", r"CS:w_0", r"dynamical dark", r"modified gravity",
        r"CS:f\(R\)", r"horndeski", r"type ia supernova\w*", r"supernova cosmology",
        r"cosmic chronometer\w*", r"distance ladder",
    ],
    "cosmo.early": [
        r"inflation(?:ary)?", r"cosmic microwave background", r"CS:CMB",
        r"primordial", r"early universe", r"reioni[sz]ation", r"21[- ]?cm",
        r"cosmic dawn", r"dark ages", r"baryogenesis", r"non-?gaussianit\w*",
        r"cosmological collider", r"big bang nucleosynthesis", r"CS:BBN",
        r"planck (?:data|satellite|mission|collaboration)", r"b-modes?",
        r"stochastic gravitational[- ]wave background",
    ],
    "cosmo.lss": [
        r"large[- ]scale structure", r"CS:LSS", r"baryon acoustic", r"CS:BAO",
        r"galaxy (?:clustering|survey\w*|bias)", r"redshift[- ]space", r"CS:RSD",
        r"weak (?:gravitational )?lensing", r"cosmic shear", r"CS:DESI",
        r"CS:Euclid", r"CS:LSST", r"rubin observatory", r"CS:S8", r"sigma_?8",
        r"matter power spectrum", r"halo model", r"n-body", r"cosmological simulation\w*",
        r"structure formation", r"intensity mapping", r"peculiar velocit\w*",
        r"field-level", r"CS:Roman Space Telescope",
    ],
    "cosmo.dm": [
        r"dark matter", r"CS:WIMPs?", r"axion\w*", r"sterile neutrino\w*",
        r"fuzzy dark", r"primordial black holes?", r"CS:PBHs?", r"dark sector",
    ],

    "ai.general": [
        r"machine learning", r"deep learning", r"neural networks?",
        r"artificial intelligence", r"CS:AI", r"representation learning",
        r"data science", r"graph neural", r"CS:GNNs?", r"CS:ML",
        r"neural information processing", r"learning representations",
        r"CS:NeurIPS", r"CS:ICML", r"CS:ICLR", r"CS:AAAI", r"CS:IJCAI",
        r"pattern recognition", r"neural computation", r"geometric deep learning",
        r"federated learning", r"continual learning", r"lifelong learning",
        r"self-supervised", r"knowledge representation", r"automated planning",
        r"evolutionary computation", r"genetic (?:algorithms?|programming)",
    ],
    "ai.genai": [
        r"CS:LLMs?", r"large language models?", r"language models?",
        r"transformers?(?! (?:substation|winding))", r"generative (?:models?|AI|modell?ing)",
        r"CS:GenAI", r"diffusion models?", r"score-based", r"foundation models?",
        r"agentic", r"(?:AI|LLM) agents?", r"prompt(?:ing| engineering)", r"in-context learning",
        r"variational auto-?encoders?", r"CS:VAEs?", r"CS:GANs?", r"generative adversarial",
        r"text-to-(?:image|video|speech)", r"CS:RAG", r"retrieval-augmented",
        r"CS:GPT", r"chatbots?", r"CS:COLM",
    ],
    "ai.nlp": [
        r"natural language(?: processing| understanding| generation)?", r"CS:NLP",
        r"computational linguistics", r"machine translation", r"speech (?:recognition|processing|synthesis)",
        r"spoken language", r"question answering", r"text (?:mining|classification|summari[sz]ation)",
        r"sentiment analysis", r"information extraction", r"CS:ACL", r"CS:EMNLP",
        r"CS:NAACL", r"CS:EACL", r"CS:COLING", r"CS:CoNLL", r"CS:LREC",
        r"interspeech", r"CS:ICASSP", r"multilingual", r"low-resource languages?",
    ],
    "ai.vision": [
        r"computer vision", r"image (?:recognition|segmentation|generation|analysis|processing|understanding)",
        r"object detection", r"visual (?:recognition|understanding|computing)",
        r"video (?:understanding|analysis|generation)", r"3-?d (?:vision|reconstruction)",
        r"multimodal", r"multi-modal", r"vision[- ]language", r"CS:CVPR", r"CS:ICCV",
        r"CS:ECCV", r"CS:WACV", r"CS:BMVC", r"CS:ICVGIP", r"CS:ACCV", r"CS:3DV",
        r"medical image\w*", r"biometrics?", r"face recognition", r"document analysis",
        r"neural radiance", r"CS:NeRFs?", r"gaussian splatting", r"remote sensing",
    ],
    "ai.rl": [
        r"reinforcement learning", r"CS:RL", r"sequential decision\w*", r"decision[- ]making under uncertainty",
        r"multi-?agent systems?", r"autonomous agents", r"Markov decision", r"CS:MDPs?",
        r"policy (?:gradient|optimi[sz]ation|learning)", r"imitation learning",
        r"offline RL", r"CS:AAMAS", r"CS:RLC", r"CS:ICAPS", r"game[- ]playing",
    ],
    "ai.trust": [
        r"(?:AI|ML) safety", r"safe (?:AI|machine learning|reinforcement learning)",
        r"(?:AI|value|model) alignment", r"interpretab\w*", r"explainab\w*", r"CS:XAI", r"fairness",
        r"responsible (?:AI|machine learning)", r"trustworthy (?:AI|machine learning|ML)",
        r"adversarial (?:examples?|attacks?|robustness)", r"CS:FAccT",
        r"privacy-preserving", r"differential(?:ly)? priva\w*", r"mechanistic interpretability", r"AI ethics",
        r"ethics (?:of|in) (?:AI|artificial intelligence)", r"AI governance", r"AI policy",
    ],
    "ai.theory": [
        r"learning theory", r"statistical learning", r"generali[sz]ation (?:bounds?|error|theory)",
        r"CS:PAC", r"kernel methods?", r"stochastic gradient", r"CS:SGD",
        r"neural tangent", r"(?:theory|mathematics) of (?:deep|machine) learning",
        r"deep learning theory", r"high-dimensional statistic\w*", r"sample complexity",
        r"online learning", r"bandits?", r"kolmogorov[- ]arnold", r"CS:KANs?",
        r"overparameteri[sz]\w*", r"implicit bias", r"compressed sensing",
        r"sparse recovery", r"bayesian (?:deep learning|neural)", r"optimal transport",
        r"mean[- ]field (?:limit|theory) of (?:neural|deep)",
        r"(?:non-?)?convex optimi[sz]ation", r"optimi[sz]ation (?:for|in) (?:machine|deep) learning",
        r"CS:COLT", r"CS:ALT", r"CS:AISTATS", r"CS:UAI", r"probabilistic (?:machine learning|AI|modell?ing)",
        r"gaussian processes?", r"neural scaling laws?", r"theory of (?:transformers|neural networks|generali[sz]ation)",
    ],
    "ai.science": [
        r"(?:machine learning|deep learning|neural networks?|CS_INLINE_AI|artificial intelligence) "
        r"(?:for|in|and|meets)(?: and (?:for|in))? (?:the )?(?:science|physics|astronomy|astrophysics|cosmology|"
        r"physical sciences|astro\w*|space|the universe|fundamental physics)",
        r"CS:ML4PS", r"CS:AI4Science", r"ai for science", r"scientific machine learning",
        r"CS:SciML", r"physics[- ]informed", r"CS:PINNs?", r"neural operators?",
        r"simulation[- ]based inference", r"CS:SBI", r"likelihood[- ]free",
        r"emulat(?:or|ors|ion)", r"surrogate models?", r"neural (?:posterior|density|likelihood) estimat\w*",
        r"normali[sz]ing flows?", r"differentiable (?:simulation|programming|physics)",
        r"symbolic regression", r"data-driven discovery", r"astroinformatics",
        r"astrostatistic\w*", r"cosmostatistic\w*",
    ],

    "cs.theory": [
        r"(?:design and analysis of|theory of|efficient|graph|approximation|online|streaming|parallel|combinatorial) algorithms?",
        r"algorithmic(?! trading)", r"(?:computational )?complexity theor\w*",
        r"theory of computation", r"theoretical computer science", r"CS:TCS",
        r"computability", r"randomi[sz]ed algorithms?",
        r"data structures?", r"computational geometry",
        r"quantum (?:algorithms?|complexity)", r"automata", r"formal languages",
        r"CS:STOC", r"CS:FOCS", r"CS:SODA", r"CS:ICALP", r"CS:FSTTCS", r"CS:SoCG", r"CS:CCC",
        r"CS:APPROX", r"CS:RANDOM", r"CS:ITCS", r"CS:STACS", r"CS:ESA", r"CS:MFCS",
        r"algorithmic game theory", r"mechanism design", r"(?:P|NP)-hard\w*", r"NP-complete\w*",
        r"pseudorandom\w*", r"property testing", r"sublinear", r"parameteri[sz]ed complexity",
        r"distributed computing", r"CS:PODC", r"CS:DISC",
    ],
    "cs.systems": [
        r"operating systems?", r"distributed systems?", r"computer systems?", r"cloud computing",
        r"computer architecture", r"high[- ]performance computing", r"CS:HPC", r"supercomput\w*",
        r"parallel (?:computing|programming|algorithms?)", r"CS:GPUs?", r"hardware accelerators?",
        r"computer networks?", r"wireless (?:networks?|communications?)",
        r"internet of things", r"CS:IoT", r"edge computing", r"embedded systems?",
        r"storage systems?", r"datacenters?", r"data cent(?:er|re)s?", r"(?:VLSI|chip|hardware) design",
        r"CS:VLSI", r"CS:FPGAs?", r"CS:MLSys", r"(?:ML|AI) systems", r"CS:OSDI", r"CS:SOSP",
        r"CS:NSDI", r"CS:SIGCOMM", r"CS:INFOCOM", r"CS:MobiCom", r"CS:ASPLOS", r"CS:ISCA",
        r"CS:MICRO", r"CS:HPCA", r"CS:EuroSys", r"CS:COMSNETS", r"CS:HiPC",
        r"cyber-?physical", r"real-time systems?", r"CS:5G", r"CS:6G",
    ],
    "cs.security": [
        r"cryptograph\w*", r"cryptolog\w*", r"(?:cyber|computer|network|information|systems?) security",
        r"cybersecurity", r"security and privacy", r"privacy", r"malware", r"blockchains?",
        r"zero-knowledge", r"homomorphic encryption", r"post-quantum", r"encryption",
        r"CS:CRYPTO", r"CS:EUROCRYPT", r"CS:ASIACRYPT", r"CS:INDOCRYPT", r"CS:CCS",
        r"CS:NDSS", r"CS:USENIX Security", r"CS:CHES", r"CS:TCC", r"CS:PETS",
        r"formal security", r"side[- ]channels?", r"secure (?:computation|systems?)",
    ],
    "cs.pl": [
        r"programming languages?", r"type (?:theory|systems?)", r"compilers?",
        r"program (?:analysis|synthesis|verification)", r"formal (?:methods|verification)",
        r"model checking", r"software engineering", r"software (?:testing|systems?|verification)",
        r"functional programming", r"concurrency theory", r"semantics of programming",
        r"CS:POPL", r"CS:PLDI", r"CS:ICFP", r"CS:OOPSLA", r"CS:CAV", r"CS:LICS",
        r"CS:ICSE", r"CS:FSE", r"CS:ESEC", r"CS:ISSTA", r"CS:ETAPS", r"CS:TACAS",
        r"proof assistants?", r"CS:Coq", r"CS:Rocq", r"CS:Isabelle", r"CS:Agda",
        r"logic in computer science", r"static analysis", r"code generation",
    ],
    "cs.data": [
        r"databases?", r"data management", r"data mining", r"knowledge discovery",
        r"information retrieval", r"recommender systems?", r"recommendation systems?",
        r"web search", r"search engines?", r"knowledge graphs?", r"big data",
        r"CS:SIGMOD", r"CS:VLDB", r"CS:ICDE", r"CS:PODS", r"CS:KDD", r"CS:SIGKDD",
        r"CS:SIGIR", r"CS:WSDM", r"CS:CIKM", r"CS:ICDM", r"CS:ECIR", r"CS:RecSys",
        r"CS:CODS", r"CS:COMAD", r"semantic web", r"data engineering", r"social networks? analysis",
        r"world wide web",
    ],
    "cs.hci": [
        r"human[- ]computer interaction", r"CS:HCI", r"user interfaces?", r"user experience",
        r"interaction design", r"ubiquitous computing", r"accessibility",
        r"computer graphics", r"CS:SIGGRAPH", r"visuali[sz]ation", r"virtual reality",
        r"augmented reality", r"mixed reality", r"CS:VR", r"CS:AR", r"CS:CHI", r"CS:UIST",
        r"CS:CSCW", r"CS:IUI", r"rendering", r"geometry processing", r"animation",
        r"computational design", r"CS:EuroVis", r"CS:Eurographics", r"video games?", r"game design",
    ],
    "cs.robotics": [
        r"robot\w*", r"autonomous (?:vehicles?|systems?|driving|navigation)", r"self-driving",
        r"drones?", r"CS:UAVs?", r"legged locomotion", r"motion planning",
        r"CS:SLAM", r"CS:ICRA", r"CS:IROS", r"CS:RSS", r"CS:CoRL", r"control systems?",
        r"embodied (?:AI|intelligence)", r"humanoids?",
    ],
    "cs.general": [
        r"computer science", r"computational thinking", r"CS:ACM",
        r"CS:IEEE Computer Society", r"informatics", r"research software", r"quantum computing",
        r"signal processing", r"information systems?", r"CS:CSE", r"CS:EECS",
        r"bioinformatics", r"computational biology",
    ],

    "astro.general": [
        r"astronom\w*", r"astrophysic\w*", r"telescopes?", r"observator(?:y|ies)",
        r"astroparticle", r"radio astronomy", r"CS:SKA", r"sky surveys?", r"CS:IAU",
        r"space mission\w*", r"astrometr\w*", r"spectroscop\w* survey",
    ],
    "astro.galactic": [
        r"galax(?:y|ies)", r"galactic", r"CS:AGNs?", r"active galactic", r"quasars?",
        r"interstellar medium", r"CS:ISM", r"circumgalactic", r"milky way",
        r"star formation", r"intracluster", r"galaxy clusters?", r"star clusters?",
    ],
    "astro.stellar": [
        r"stellar", r"exoplanet\w*", r"planetary (?:system|science|formation)\w*",
        r"protoplanetary", r"asteroseismolog\w*", r"solar (?:physics|flares?|wind|corona|dynamo|system)",
        r"heliophys\w*", r"white dwarfs?", r"binary stars?", r"supernova(?:e|s)?",
        r"nucleosynthesis", r"small bodies", r"comets?", r"asteroids?", r"space weather",
        r"massive stars?", r"stars and planets", r"CS:Aditya",
    ],
    "astro.he": [
        r"black holes?", r"neutron stars?", r"pulsars?", r"magnetars?",
        r"gamma[- ]rays?", r"x-ray (?:astronomy|binar\w*|sources?|observ\w*)",
        r"cosmic rays?", r"gravitational[- ]waves?", r"CS:LIGO", r"CS:LISA",
        r"fast radio bursts?", r"CS:FRBs?", r"astrophysical transients", r"time[- ]domain",
        r"tidal disruption", r"kilonova\w*", r"compact objects?", r"accretion",
        r"CS:GRBs?", r"multi-?messenger", r"relativistic jets?",
        r"(?:hybrid|compact|quark|strange|neutron) stars?", r"dense matter", r"relativistic astrophysics",
    ],

    "math.nt": [
        r"number theor\w*", r"arithmetic (?:geometry|statistics|topology|of)",
        r"modular forms?", r"automorphic", r"CS:L-functions?", r"l-functions?",
        r"zeta (?:functions?|values)", r"diophantine", r"galois representations?",
        r"elliptic curves?", r"p-adic", r"iwasawa", r"langlands", r"class field",
        r"eisenstein", r"abelian variet\w*", r"(?:cubic|quadratic|number) fields",
        r"analytic number", r"sieve methods?", r"mahler measure", r"modularity",
        r"primes?(?! minister)", r"hecke", r"shimura", r"ramanujan", r"stark units?",
        r"(?:cubic|quadratic|abelian|galois|cyclotomic) extensions?", r"additive bases",
        r"h-bases", r"arithmetic statistics", r"CS:CM-types?", r"complex multiplication",
    ],
    "math.topology": [
        r"topolog\w*(?! (?:insulator|phase|order|matter|superconduct|quantum|photonic|materials))",
        r"homotop\w*", r"homolog\w*", r"cohomolog\w*", r"knots?(?! per)", r"knot theory",
        r"manifolds?", r"CS:TQFTs?", r"cobordism", r"fundamental groups?",
        r"mapping class", r"[34]-manifolds?", r"sheaf|sheaves", r"persistent homology",
        r"loop spaces?",
    ],
    "math.algebra": [
        r"algebras?(?! for tensors)", r"algebraic(?! (?:geometry|topology|number))", r"group theor\w*",
        r"group (?:schemes?|actions?|representations?|cohomology)",
        r"(?:finite|lie|free|discrete|abelian|reductive|algebraic|quantum) groups?",
        r"representation theor\w*", r"commutative algebra", r"noncommutative",
        r"rings? and modules", r"lie (?:algebras?|groups?|theory)", r"category theor\w*",
        r"categorical", r"hopf", r"quivers?", r"homological algebra", r"galois theory",
        r"cluster algebras?", r"operads?", r"koszul", r"vertex operator", r"2-groups?",
    ],
    "math.geometry": [
        r"geometr(?:y|ies|ic)(?! deep learning)", r"algebraic geometry", r"differential geometry",
        r"riemannian", r"symplectic", r"calabi[- ]yau", r"moduli", r"curvature",
        r"minimal surfaces?", r"hodge", r"k(?:ä|a)hler", r"mirror symmetry", r"spinors?",
        r"monopoles?", r"orbifolds?", r"varieties", r"surfaces of",
    ],
    "math.analysis": [
        r"(?:functional|harmonic|complex|real|fourier|microlocal|spectral|nonlinear|numerical) analysis",
        r"partial differential equations?", r"CS:PDEs?", r"differential equations?",
        r"operator (?:algebras?|theory)", r"heat kernels?", r"dirichlet forms?", r"sobolev",
        r"inequalit(?:y|ies)", r"dispersive", r"navier[- ]stokes", r"calculus of variations",
        r"approximation theory", r"integral (?:equations?|representations?)", r"analytification",
        r"amenab\w*", r"ergodic", r"schr(?:ö|o)dinger equations?", r"blow-?up",
    ],
    "math.probability": [
        r"probabilit\w*", r"stochastic\w*", r"random (?:matri\w*|walks?|graphs?|fields?|processes)",
        r"brownian", r"markov", r"martingales?",
        r"statistic\w*(?! (?:mechanic|physic))", r"bayesian", r"statistical inference",
        r"causal inference", r"large deviations?", r"percolation", r"extreme values?",
        r"fokker[- ]planck", r"regression", r"monte carlo", r"uncertainty quantification",
        r"spin glass\w*",
    ],
    "math.mathphys": [
        r"mathematical physics", r"integrable (?:systems?|models?|hierarch\w*)",
        r"lax (?:pairs?|representation)", r"conformal field theor\w*", r"vertex algebras?",
        r"CS:TQFTs?", r"mathematical relativity", r"spectral theory",
        r"quantum field theor\w* (?:mathematic\w*|rigorous)",
    ],
    "math.other": [
        r"mathemat\w*", r"combinatori\w*", r"graph theor\w*", r"mathematical logic",
        r"model theory", r"set theory", r"g(?:ö|o)del", r"incompleteness", r"proof theory",
        r"dynamical systems?", r"game theory", r"optimal control", r"convex optimi[sz]ation",
        r"numerical methods?", r"information theor\w*", r"coding theory", r"cryptograph\w*",
        r"formal(?:i[sz]ed|i[sz]ation)? (?:proofs?|mathematics)", r"theorem prov\w*",
        r"CS:Lean", r"posets?", r"history of mathematics", r"chaos",
    ],

    "phys.gr": [
        r"general relativity", r"gravitation\w*", r"gravity", r"spacetimes?", r"space-time",
        r"einstein", r"wormholes?", r"numerical relativity", r"quantum gravity",
        r"tidal deformation", r"geodesics?", r"black holes?", r"CS:gr-qc",
    ],
    "phys.hepth": [
        r"string theor\w*", r"string field", r"worldsheet", r"superstrings?",
        r"quantum field theor\w*", r"CS:QFTs?", r"gauge theor\w*", r"supersymmetr\w*",
        r"CS:SUSY", r"holograph\w*", r"CS:AdS", r"CS:CFTs?", r"conformal (?:field|bootstrap)",
        r"scattering amplitudes?", r"infrared divergences?", r"generali[sz]ed symmetr\w*",
        r"higher[- ]form symmetr\w*", r"higher symmetr\w*", r"particle physics",
        r"high[- ]energy physics", r"CS:HEP", r"phenomenolog\w*", r"colliders?",
        r"CS:LHC", r"neutrinos?", r"standard model", r"beyond the standard model",
        r"CS:BSM", r"effective field theor\w*", r"CS:EFTs?", r"CS:QCD", r"hadron\w*",
        r"swampland", r"anomal(?:y|ies) (?:inflow|matching)", r"nambu",
    ],
    "phys.quantum": [
        r"quantum (?:information|computing|computation|matter|many-body|chaos|optics|"
        r"mechanics|entanglement|technolog\w*|devices?|sensing|simulation|thermodynamics)",
        r"entanglement", r"qubits?", r"open quantum", r"decoherence", r"semiclassical",
        r"classical and quantum",
    ],
    "phys.condmat": [
        r"condensed matter", r"spin glass\w*", r"statistical (?:mechanics|physics)",
        r"phase transitions?", r"topological (?:insulators?|phases?|matter|order)",
        r"superconduct\w*", r"(?:frustrated|quantum|itinerant) magnetism", r"magnetic materials", r"spin (?:chains?|liquids?|systems?)",
        r"soft matter", r"active matter", r"living matter", r"polymers?",
        r"biological physics", r"biophysics", r"non-?equilibrium", r"many-body",
        r"glass(?:es|y)?(?! ceiling)", r"fluctuation theory", r"quantum matter",
    ],
    "phys.fluids": [
        r"turbulen\w*", r"fluids?", r"plasmas?", r"hydrodynamic\w*",
        r"magnetohydrodynamic\w*", r"CS:MHD", r"convection",
        r"(?<!normalizing )(?<!normalising )flows?(?! matching|-based| models?)", r"climate (?:dynamics|physics|model\w*|chaos)", r"atmospher\w*",
        r"ocean\w*", r"stochasticity", r"diffusion(?! models?| and flow|-based)",
    ],
    "phys.general": [
        r"physics", r"optic(?:s|al)", r"photon\w*", r"lasers?",
        r"nuclear (?:physics|structure|theory|matter)", r"atomic", r"acoustic\w*",
        r"polari[sz]ation", r"caustics", r"water",
    ],
}

# ---------------------------------------------------------------------------
# Declared subject codes -> sub-fields (with evidence weight)
# Codes are normalised: lowercase, '.', '-', ' ' -> '_'.
# ---------------------------------------------------------------------------
STRONG, MEDIUM, WEAK = 1.5, 1.0, 0.6

_ARXIV_MATH = {
    "nt": "math.nt",
    "at": "math.topology", "gt": "math.topology", "gn": "math.topology",
    "kt": "math.topology",
    "ra": "math.algebra", "ac": "math.algebra", "rt": "math.algebra",
    "gr": "math.algebra", "qa": "math.algebra", "ct": "math.algebra",
    "ag": "math.geometry", "dg": "math.geometry", "mg": "math.geometry",
    "sg": "math.geometry", "cv": "math.analysis",
    "ap": "math.analysis", "ca": "math.analysis", "fa": "math.analysis",
    "oa": "math.analysis", "sp": "math.analysis", "na": "math.analysis",
    "pr": "math.probability", "st": "math.probability",
    "mp": "math.mathphys",
    "ds": "math.other", "co": "math.other", "lo": "math.other", "oc": "math.other",
    "it": "math.other", "gm": "math.other", "ho": "math.other",
}


# arXiv computer-science / EESS categories (researchseminars.org uses the same codes)
_ARXIV_CS = {
    "cs_lg": "ai.general", "cs_ai": "ai.general", "cs_ne": "ai.general",
    "cs_cv": "ai.vision", "eess_iv": "ai.vision",
    "cs_cl": "ai.nlp", "cs_sd": "ai.nlp", "eess_as": "ai.nlp",
    "cs_ma": "ai.rl",
    "cs_cc": "cs.theory", "cs_ds": "cs.theory", "cs_fl": "cs.theory", "cs_cg": "cs.theory",
    "cs_dm": "cs.theory", "cs_gt": "cs.theory",
    "cs_dc": "cs.systems", "cs_os": "cs.systems", "cs_ni": "cs.systems", "cs_ar": "cs.systems",
    "cs_pf": "cs.systems", "cs_et": "cs.systems",
    "cs_cr": "cs.security",
    "cs_pl": "cs.pl", "cs_se": "cs.pl", "cs_lo": "cs.pl",
    "cs_db": "cs.data", "cs_ir": "cs.data", "cs_dl": "cs.data", "cs_si": "cs.data",
    "cs_hc": "cs.hci", "cs_gr": "cs.hci", "cs_mm": "cs.hci",
    "cs_ro": "cs.robotics",
    "cs_na": "math.analysis", "cs_it": "math.other",
}

# Topic tags of the CS aggregators: huggingface/ai-deadlines tags, ccf-deadlines
# areas ("ccf_<area>") and awesome-mlss school topics ("mlss_<topic>").
_CODES = {}
for _sf, _w, _codes in [
    ("ai.theory", STRONG, ["stat_ml", "cs_lg_theory", "optimization_methods", "learning_theory",
                           "mlss_theory"]),
    ("ai.general", STRONG, ["machine_learning", "deep_learning", "representation_learning",
                            "lifelong_learning", "knowledge_representation", "reasoning",
                            "mlss_ml", "mlss_kr", "mlss_cogsci", "mlss_neuro", "mlss_eml",
                            "mlss_health", "mlss_econai", "mlss_ds"]),
    ("ai.genai", STRONG, ["large_language_models", "mlss_genai"]),
    ("ai.nlp", STRONG, ["natural_language_processing", "speech", "mlss_nlp", "mlss_sp"]),
    ("ai.vision", STRONG, ["computer_vision", "image_processing", "pattern_recognition",
                           "visual_information_processing", "mlss_cv"]),
    ("ai.rl", STRONG, ["reinforcement_learning", "mlss_rl", "mlss_ap", "mlss_ai4games"]),
    ("ai.trust", STRONG, ["fairness", "mlss_rai"]),
    ("ai.science", STRONG, ["mlss_ml4science", "mlss_bio"]),
    ("ai.general", MEDIUM, ["ccf_ai", "mlss_quantum"]),
    ("phys.quantum", MEDIUM, ["mlss_quantum"]),
    ("cs.theory", STRONG, ["ccf_ct"]),
    ("cs.systems", STRONG, ["ccf_ds", "ccf_nw", "mlss_hw"]),
    ("cs.security", STRONG, ["ccf_sc"]),
    ("cs.pl", STRONG, ["ccf_se", "software_engineering"]),
    ("cs.data", STRONG, ["ccf_db", "data_mining", "web_search", "information_retrieval",
                         "information_systems", "knowledge_graphs", "recommendation",
                         "retrieval", "web_mining", "content_analysis",
                         "semantics_and_knowledge", "mlss_dm", "mlss_recsys"]),
    ("cs.hci", STRONG, ["ccf_cg", "ccf_hi", "computer_graphics", "human_computer_interaction",
                        "mlss_cg", "mlss_hci"]),
    ("cs.robotics", STRONG, ["robotics", "mlss_ro"]),
    ("cs.general", MEDIUM, ["ccf_mx", "signal_processing"]),
    ("math.other", MEDIUM, ["mlss_log"]),
]:
    for _c in _codes:
        _CODES.setdefault(_c, []).append((_sf, _w))


def declared_codes(code):
    """Map one declared subject code -> list of (subfield, weight)."""
    raw = str(code).strip()
    if raw.startswith("field:"):             # chosen by YOU in watchlist.yaml
        f = raw[6:].strip()
        if f in SUBFIELDS:
            return [(f, STRONG)]
        if f in FIELDS:
            return [(next(s for s, v in SUBFIELDS.items()
                          if v[0] == f and s.endswith((".general", ".other"))), STRONG)]
        raw = f
    c = re.sub(r"[.\- ]+", "_", raw.lower())
    out = []
    # arXiv-style math codes: math_NT, math.NT
    m = re.match(r"^math_([a-z]{2})$", c)
    if m and m.group(1) in _ARXIV_MATH:
        return [(_ARXIV_MATH[m.group(1)], STRONG)]
    if c in ("math", "mathematics"):
        return [("math.other", WEAK)]
    if c in ("math_ph", "math_mp", "physics_math_ph", "math_and_math_physics"):
        return [("math.mathphys", STRONG)]
    # astro
    if c in ("astro_ph_co", "astro_co", "physics_astro_ph_co", "cosmology",
             "cosmology_and_nongalactic_astrophysics"):
        return [("cosmo.general", STRONG), ("astro.general", WEAK)]
    if c in ("astro_ph_ga", "astro_ga", "physics_astro_ph_ga"):
        return [("astro.galactic", STRONG)]
    if c in ("astro_ph_he", "astro_he", "physics_astro_ph_he"):
        return [("astro.he", STRONG)]
    if c in ("astro_ph_sr", "astro_ph_ep", "astro_sr", "astro_ep",
             "physics_astro_ph_sr", "physics_astro_ph_ep"):
        return [("astro.stellar", STRONG)]
    if c in ("astro_ph_im", "astro_im", "physics_astro_ph_im"):
        return [("astro.general", STRONG)]
    if c.startswith("astro") or c == "astrophysics":
        return [("astro.general", STRONG)]
    # physics
    if c in ("gr_qc", "physics_gr_qc", "general_relativity"):
        return [("phys.gr", STRONG)]
    if c == "gravitation_and_cosmology":           # INSPIRE category
        return [("phys.gr", STRONG), ("cosmo.general", WEAK)]
    if c in ("hep_th", "physics_hep_th", "theory_hep", "hep_ph", "physics_hep_ph",
             "phenomenology_hep", "hep_lat", "lattice"):
        return [("phys.hepth", STRONG)]
    if c in ("hep_ex", "experiment_hep", "experiment_nucl", "theory_nucl",
             "nucl_th", "nucl_ex", "general_physics", "physics_optics",
             "physics_atom_ph", "instrumentation", "accelerators"):
        return [("phys.general", MEDIUM)]
    if c in ("quant_ph", "physics_quant_ph", "quantum_physics"):
        return [("phys.quantum", STRONG)]
    if c.startswith(("cond_mat", "physics_cond_mat")) or c == "condensed_matter":
        return [("phys.condmat", STRONG)]
    if c in ("physics_flu_dyn", "physics_plasm_ph", "physics_ao_ph", "nlin_cd"):
        return [("phys.fluids", STRONG)]
    if c.startswith("nlin"):
        return [("math.mathphys", MEDIUM)]
    if c in ("physics",):
        return [("phys.general", WEAK)]
    if c == "data_analysis_and_statistics":        # INSPIRE category
        return [("math.probability", WEAK)]
    # CS / stats / AI
    if c in _CODES:
        return list(_CODES[c])
    m = re.match(r"^(?:cs|eess)_([a-z]{2})$", c)
    if m and m.group(0) in _ARXIV_CS:
        return [(_ARXIV_CS[m.group(0)], STRONG)]
    if c in ("stat", "stat_th", "stat_me", "stat_ap", "stat_co", "math_st"):
        return [("math.probability", STRONG)]
    if c.startswith(("cs_", "eess_")) or c in ("cs", "computer_science"):
        return [("cs.general", MEDIUM)]
    return out


# ---------------------------------------------------------------------------
# Embedding prototypes (Option B). A few sentences that describe what an
# event on this sub-field *sounds like*. Negative classes absorb events that
# are about something else entirely, so they don't get forced into a field.
# ---------------------------------------------------------------------------
PROTOTYPES = {
    "cosmo.de": "dark energy, cosmic acceleration, Hubble tension, expansion history of the universe, modified gravity, supernova cosmology, DESI BAO constraints on w0 wa",
    "cosmo.lss": "large-scale structure of the universe, galaxy clustering, weak lensing, cosmic shear, redshift surveys, cosmological N-body simulations, matter power spectrum",
    "cosmo.early": "cosmic microwave background, inflation, primordial non-Gaussianity, reionization, 21-cm cosmology, early universe physics",
    "cosmo.dm": "dark matter particles, axions, primordial black holes, dark matter halos and direct detection",
    "cosmo.general": "cosmology conference, physical cosmology, the standard cosmological model, observational cosmology",
    "ai.science": "machine learning for physics and astronomy, simulation-based inference, neural emulators, AI for science, physics-informed neural networks",
    "ai.theory": "theory of deep learning, statistical learning theory, generalization bounds, optimization, kernel methods, learning theory",
    "ai.genai": "large language models, generative models, diffusion models, foundation models, transformers, LLM agents, generative AI",
    "ai.nlp": "natural language processing, computational linguistics, machine translation, speech recognition, question answering",
    "ai.vision": "computer vision, image recognition, object detection, video understanding, multimodal vision-language models, 3D reconstruction",
    "ai.rl": "reinforcement learning, sequential decision making, multi-agent systems, planning, bandits and control, imitation learning",
    "ai.trust": "AI safety, alignment, interpretability, fairness, privacy and robustness of machine learning, responsible AI",
    "ai.general": "machine learning conference, deep learning, neural networks, representation learning, artificial intelligence research",
    "cs.theory": "algorithms, computational complexity, theoretical computer science, approximation and randomized algorithms, data structures",
    "cs.systems": "operating systems, distributed systems, computer architecture, networking, high-performance computing, cloud and edge computing",
    "cs.security": "computer security, cryptography, privacy, network security, malware, blockchain, secure systems",
    "cs.pl": "programming languages, compilers, type systems, formal verification, model checking, software engineering",
    "cs.data": "databases, data management, data mining, information retrieval, recommender systems, web search, knowledge graphs",
    "cs.hci": "human-computer interaction, user interfaces, computer graphics, visualization, virtual and augmented reality",
    "cs.robotics": "robotics, autonomous vehicles, robot learning, manipulation and locomotion, motion planning, drones",
    "cs.general": "computer science department seminar, computing research, informatics, signal processing, information systems",
    "astro.he": "black holes, neutron stars, pulsars, gravitational wave astronomy, gamma-ray bursts, high-energy astrophysics, transients",
    "astro.galactic": "galaxy formation and evolution, active galactic nuclei, interstellar medium, star formation, galaxy clusters",
    "astro.stellar": "stellar physics, the Sun, solar flares, exoplanets, planetary systems, asteroseismology, supernovae",
    "astro.general": "astronomy and astrophysics meeting, telescopes, observatories, sky surveys, radio astronomy",
    "math.nt": "number theory, modular forms, L-functions, elliptic curves, Galois representations, arithmetic geometry, primes",
    "math.topology": "algebraic topology, low-dimensional topology, homotopy theory, knots, manifolds, cohomology",
    "math.algebra": "algebra, representation theory, group theory, Lie algebras, category theory, commutative algebra",
    "math.geometry": "differential geometry, algebraic geometry, symplectic geometry, moduli spaces, Riemannian geometry",
    "math.probability": "probability theory, stochastic processes, random matrices, Brownian motion, mathematical statistics, Bayesian inference",
    "math.mathphys": "mathematical physics, integrable systems, conformal field theory, rigorous quantum field theory",
    "math.analysis": "analysis, partial differential equations, harmonic analysis, functional analysis, operator theory",
    "math.other": "combinatorics, mathematical logic, dynamical systems, graph theory, discrete mathematics",
    "phys.gr": "general relativity, gravitation, spacetime geometry, black hole physics, numerical relativity, quantum gravity",
    "phys.hepth": "string theory, quantum field theory, particle physics, holography, scattering amplitudes, gauge theories",
    "phys.quantum": "quantum information, quantum computing, entanglement, quantum many-body physics, quantum optics",
    "phys.condmat": "condensed matter physics, statistical mechanics, soft matter, active matter, phase transitions, superconductivity",
    "phys.fluids": "fluid dynamics, turbulence, plasma physics, magnetohydrodynamics, climate and atmospheric physics",
    "phys.general": "physics colloquium, optics, lasers, atomic and nuclear physics",
}
NEGATIVE_PROTOTYPES = {
    "neg.bio": "biology, medicine, genomics, neuroscience, cell biology, clinical research, ecology",
    "neg.chem": "chemistry, materials synthesis, catalysis, batteries, chemical engineering",
    "neg.eng": "power systems, electrical machines, civil and mechanical engineering, manufacturing, construction, automotive industry",
    "neg.admin": "committee meeting, foundation day, cultural event, open day, inauguration ceremony, administrative announcement, alumni event",
    "neg.humanities": "history, philosophy, economics, social sciences, education policy, arts and culture",
}


# ---------------------------------------------------------------------------
# Compilation helpers
# ---------------------------------------------------------------------------
def _compile(pattern):
    if pattern.startswith("CS:"):
        return re.compile(W + pattern[3:] + W)
    pattern = pattern.replace("CS_INLINE_AI", "AI")
    return re.compile(W + "(?:" + pattern + ")" + W, re.I)


COMPILED = {sf: [_compile(p) for p in pats] for sf, pats in RULES.items()}


def parent(sf):
    return SUBFIELDS[sf][0]


def label(node):
    return FIELDS[node] if node in FIELDS else SUBFIELDS[node][1]


def is_node(node):
    """A taxonomy node a profile may weight: a field or a sub-field."""
    return node in FIELDS or node in SUBFIELDS


def ancestors(node):
    """The node itself, then its ancestors up to the field (most specific first)."""
    return [node] if node in FIELDS else [node, SUBFIELDS[node][0]]


ORDER = {sf: i for i, sf in enumerate(SUBFIELDS)}   # display order of sub-fields


def export_for_frontend():
    """The site builds its field/sub-field filter from this, so the
    taxonomy is defined in exactly one place."""
    return {
        "fields": [{"id": f, "label": lbl,
                    "subfields": [{"id": sf, "label": v[1]}
                                  for sf, v in SUBFIELDS.items() if v[0] == f]}
                   for f, lbl in FIELDS.items()],
    }
