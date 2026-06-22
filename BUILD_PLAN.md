# Damona container build plan — institution cluster wishlist

Source: `TODO.single.sorted` (ranked by a download+stars popularity score). These are tools used on the institution cluster, i.e. expected to be useful for end-users.

## Scope

- **405 tools** to package (all have a Bioconda recipe → straightforward micromamba-based Singularity builds).
- Already in Damona (pruned from this plan): `trimmomatic`, `varscan`, `aragorn`.
- 334 wishlist entries had **no Bioconda recipe** and are excluded here (would need source builds; revisit later).

## Build workflow (per tool)

Follow the standard recipe workflow:
1. `damona/software/<name>/Singularity.<name>_<version>` — micromamba base (`micromamba_2.5.0.img`), install latest version from Bioconda, full cleanup block.
2. `damona/software/<name>/environment.yml` (or inline) pinning the version.
3. `damona/software/<name>/registry.yaml` — placeholder release; fill `download`/`md5sum`/`doi`/`filesize` after Zenodo upload.
4. Global `registry.yaml` + `README.rst` regenerate via pre-commit hooks (do not hand-edit).

## Priorities

Build top-down by tier. Within a tier, table is ordered by popularity score.

### Tier 1 — flagship (score ≥ 8.0) — 13 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 8.73 | 437482 | 1228 | `foldseek` | steineggerlab/foldseek |
| 8.45 | 460370 | 617 | `hhsuite` | soedinglab/hh-suite |
| 8.40 | 972985 | 257 | `hyphy` | veg/hyphy |
| 8.29 | 841949 | 233 | `dendropy` | jeetsukumaran/DendroPy |
| 8.25 | 259938 | 676 | `vcflib` | vcflib/vcflib |
| 8.24 | 593912 | 293 | `sortmerna` | sortmerna/sortmerna |
| 8.20 | 394808 | 404 | `metaphlan` | biobakery/metaphlan |
| 8.19 | 287332 | 543 | `sourmash` | sourmash-bio/sourmash |
| 8.19 | 423281 | 365 | `fgbio` | fulcrumgenomics/fgbio |
| 8.11 | 216398 | 597 | `gtdbtk` | Ecogenomics/GTDBTk |
| 8.11 | 449282 | 285 | `primer3` | primer3-org/primer3 |
| 8.05 | 236738 | 470 | `rsem` | deweylab/RSEM |
| 8.02 | 162165 | 639 | `bioawk` | lh3/bioawk |

### Tier 2 — high demand (7.5–8.0) — 24 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 8.00 | 1039028 | 95 | `sepp` | smirarab/sepp |
| 7.92 | 114157 | 731 | `eggnog-mapper` | eggnogdb/eggnog-mapper |
| 7.92 | 142218 | 583 | `snippy` | tseemann/snippy |
| 7.91 | 35113 | 2301 | `transit` | simongog/sdsl-lite |
| 7.85 | 296395 | 237 | `cooler` | open2c/cooler |
| 7.83 | 137902 | 491 | `abricate` | tseemann/abricate |
| 7.81 | 220995 | 294 | `pyfastx` | lmdu/pyfastx |
| 7.81 | 332856 | 192 | `paml` | abacus-gene/paml |
| 7.77 | 214260 | 271 | `hicexplorer` | deeptools/HiCExplorer |
| 7.76 | 347541 | 164 | `cooltools` | mirnylab/cooltools |
| 7.76 | 236495 | 240 | `samblaster` | GregoryFaust/samblaster |
| 7.74 | 187157 | 291 | `barrnap` | tseemann/barrnap |
| 7.70 | 177827 | 278 | `mothur` | mothur/mothur |
| 7.69 | 192823 | 251 | `treetime` | neherlab/treetime |
| 7.68 | 158635 | 304 | `genomad` | apcamargo/genomad |
| 7.68 | 1342329 | 35 | `fasttree` | morgannprice/fasttree |
| 7.67 | 190838 | 243 | `humann` | biobakery/humann |
| 7.64 | 97751 | 446 | `bismark` | FelixKrueger/Bismark |
| 7.63 | 82344 | 515 | `anvio` | merenlab/anvio |
| 7.62 | 136468 | 302 | `kaiju` | bioinformatics-centre/kaiju |
| 7.59 | 111492 | 345 | `bracken` | jenniferlu717/Bracken |
| 7.55 | 136628 | 259 | `trimal` | inab/trimal |
| 7.54 | 102778 | 337 | `drep` | MrOlm/drep |
| 7.51 | 107550 | 298 | `ppanggolin` | labgem/PPanGGOLiN |

### Tier 3 — strong (7.0–7.5) — 49 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 7.50 | 126855 | 247 | `famsa` | refresh-bio/FAMSA |
| 7.42 | 289798 | 89 | `trnascan-se` | UCSC-LoweLab/tRNAscan-SE |
| 7.40 | 64470 | 386 | `picrust2` | picrust/picrust2 |
| 7.39 | 64828 | 378 | `roary` | sanger-pathogens/Roary |
| 7.39 | 71064 | 342 | `lumpy-sv` | arq5x/lumpy-sv |
| 7.39 | 84557 | 287 | `graphaligner` | maickrau/GraphAligner |
| 7.38 | 111577 | 213 | `metamdbg` | GaetanBenoitDev/metaMDBG |
| 7.37 | 85390 | 273 | `masurca` | alekseyzimin/masurca |
| 7.36 | 117998 | 194 | `phyml` | stephaneguindon/phyml |
| 7.36 | 57947 | 396 | `coverm` | wwood/coverm |
| 7.35 | 108339 | 206 | `metaeuk` | soedinglab/metaeuk |
| 7.35 | 180872 | 122 | `minced` | ctSkennerton/minced |
| 7.35 | 102422 | 216 | `gubbins` | nickjcroucher/gubbins |
| 7.34 | 115503 | 187 | `ariba` | sanger-pathogens/ariba |
| 7.34 | 7881 | 2746 | `colabfold` | sokrypton/ColabFold |
| 7.31 | 56747 | 356 | `panaroo` | gtonkinhill/panaroo |
| 7.30 | 100188 | 198 | `staramr` | phac-nml/staramr |
| 7.29 | 69695 | 278 | `snp-sites` | sanger-pathogens/snp-sites |
| 7.28 | 28464 | 675 | `cactus` | ComparativeGenomicsToolkit/cactus |
| 7.28 | 99797 | 188 | `mashtree` | lskatz/mashtree |
| 7.27 | 91269 | 201 | `breseq` | barricklab/breseq |
| 7.24 | 52268 | 332 | `dram` | shafferm/DRAM |
| 7.23 | 68659 | 246 | `asciigenome` | dariober/ASCIIGenome |
| 7.22 | 65357 | 255 | `antismash` | antismash/antismash |
| 7.22 | 179745 | 92 | `pairix` | 4dn-dcic/pairix |
| 7.22 | 59979 | 275 | `centrifuge` | DaehwanKimLab/centrifuge |
| 7.20 | 60857 | 259 | `shovill` | tseemann/shovill |
| 7.18 | 30843 | 493 | `pggb` | pangenome/pggb |
| 7.18 | 101052 | 149 | `chewbbaca` | B-UMMI/chewBBACA |
| 7.14 | 52895 | 261 | `rasusa` | mbhall88/rasusa |
| 7.13 | 56756 | 236 | `repeatmodeler` | Dfam-consortium/RepeatModeler |
| 7.09 | 45371 | 272 | `gffcompare` | gpertea/gffcompare |
| 7.08 | 77593 | 155 | `snp-dists` | tseemann/snp-dists |
| 7.07 | 102271 | 113 | `spaln` | ogotoh/spaln |
| 7.07 | 65803 | 176 | `pindel` | genome/pindel |
| 7.06 | 39586 | 291 | `pbipa` | PacificBiosciences/pbbioconda |
| 7.06 | 81878 | 138 | `concoct` | BinPro/CONCOCT |
| 7.06 | 52891 | 214 | `ltr_retriever` | oushujun/LTR_retriever |
| 7.05 | 46550 | 241 | `beast` | beast-dev/beast-mcmc |
| 7.04 | 90314 | 121 | `clonalframeml` | xavierdidelot/ClonalFrameML |
| 7.04 | 96495 | 113 | `lofreq` | CSB5/lofreq |
| 7.04 | 50618 | 215 | `wfmash` | waveygang/wfmash |
| 7.04 | 252384 | 42 | `portcullis` | maplesond/portcullis |
| 7.03 | 39832 | 271 | `dca` | theislab/dca |
| 7.03 | 68576 | 154 | `parsnp` | marbl/parsnp |
| 7.02 | 51428 | 204 | `pharokka` | gbouras13/pharokka |
| 7.01 | 68972 | 148 | `any2fasta` | tseemann/any2fasta |
| 7.01 | 60863 | 166 | `phylophlan` | biobakery/phylophlan |
| 7.01 | 40826 | 247 | `mhcflurry` | openvax/mhcflurry |

### Tier 4 — solid (6.5–7.0) — 63 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 6.98 | 64876 | 147 | `swarm` | torognes/swarm |
| 6.96 | 26800 | 342 | `trycycler` | rrwick/Trycycler |
| 6.96 | 42857 | 212 | `ldblockshow` | BGI-shenzhen/LDBlockShow |
| 6.96 | 36454 | 248 | `chopper` | wdecoster/chopper |
| 6.95 | 22152 | 402 | `gemma` | genetics-statistics/GEMMA |
| 6.94 | 65272 | 133 | `pyseer` | mgalardini/pyseer |
| 6.94 | 36346 | 236 | `recon` | Dfam-consortium/RepeatModeler |
| 6.92 | 21943 | 380 | `interproscan` | ebi-pf-team/interproscan |
| 6.92 | 65802 | 126 | `pbccs` | PacificBiosciences/unanimity |
| 6.92 | 76243 | 108 | `poppunk` | bacpop/PopPUNK |
| 6.90 | 69610 | 114 | `wisecondorx` | CenterForMedicalGeneticsGhent/wisecondorX |
| 6.90 | 205121 | 38 | `gofasta` | cov-ert/gofasta |
| 6.90 | 59259 | 132 | `idba` | loneknightpy/idba |
| 6.89 | 49057 | 158 | `weblogo` | WebLogo/weblogo |
| 6.89 | 50286 | 154 | `wiggletools` | Ensembl/WiggleTools |
| 6.86 | 29626 | 241 | `aster` | chaoszhang/ASTER |
| 6.85 | 26694 | 265 | `mrbayes` | NBISweden/MrBayes |
| 6.85 | 14999 | 468 | `metawrap` | bxlab/metaWRAP |
| 6.84 | 43655 | 159 | `seqwish` | ekg/seqwish |
| 6.83 | 29761 | 225 | `admixtools` | DReichLab/AdmixTools |
| 6.82 | 59458 | 110 | `toulligqc` | GenomicParisCentre/toulligQC |
| 6.81 | 77394 | 83 | `phispy` | linsalrob/PhiSpy |
| 6.81 | 184372 | 34 | `prank` | ariloytynoja/prank-msa |
| 6.80 | 49772 | 126 | `skesa` | ncbi/SKESA |
| 6.79 | 93810 | 65 | `gappa` | lczech/gappa |
| 6.79 | 24674 | 249 | `gfatools` | lh3/gfatools |
| 6.78 | 25942 | 229 | `metagraph` | ratschlab/metagraph |
| 6.77 | 11044 | 531 | `relion` | 3dem/relion |
| 6.76 | 33350 | 173 | `das_tool` | cmks/DAS_Tool |
| 6.76 | 19853 | 291 | `genomicconsensus` | PacificBiosciences/pbbioconda |
| 6.76 | 41273 | 138 | `kleborate` | klebgenomics/Kleborate |
| 6.75 | 12084 | 469 | `figtree` | rambaut/figtree |
| 6.75 | 58565 | 94 | `preseq` | smithlabcode/preseq |
| 6.74 | 19734 | 279 | `tetranscripts` | mhammell-laboratory/TEtranscripts |
| 6.71 | 25362 | 201 | `genrich` | jsh58/Genrich |
| 6.70 | 24710 | 201 | `eigensoft` | DReichLab/EIG |
| 6.69 | 48269 | 101 | `virsorter` | simroux/VirSorter |
| 6.68 | 34608 | 137 | `dnaapler` | gbouras13/dnaapler |
| 6.68 | 115646 | 40 | `upimapi` | iquasere/UPIMAPI |
| 6.65 | 30908 | 145 | `gotree` | evolbioinfo/gotree |
| 6.64 | 16858 | 257 | `checkm2` | chklovski/CheckM2 |
| 6.63 | 83314 | 50 | `mykrobe` | iqbal-lab/Mykrobe-predictor |
| 6.62 | 30105 | 139 | `nanoq` | esteinig/nanoq |
| 6.62 | 33644 | 122 | `gfastats` | vgl-hub/gfastats |
| 6.59 | 26668 | 145 | `hla-la` | DiltheyLab/HLA-LA |
| 6.59 | 56885 | 67 | `fibertools-rs` | fiberseq/fibertools-rs |
| 6.58 | 31391 | 121 | `platon` | oschwengers/platon |
| 6.58 | 40138 | 94 | `lighter` | mourisl/Lighter |
| 6.57 | 38212 | 97 | `chromhmm` | jernst98/ChromHMM |
| 6.56 | 41715 | 87 | `phanotate` | deprekate/PHANOTATE |
| 6.56 | 31374 | 116 | `sickle` | mloesch/sickle |
| 6.56 | 16842 | 216 | `scoary` | AdmiralenOla/Scoary |
| 6.55 | 35026 | 101 | `referenceseeker` | oschwengers/referenceseeker |
| 6.55 | 56795 | 61 | `kaptive` | klebgenomics/Kaptive |
| 6.55 | 18038 | 194 | `vibrant` | AnantharamanLab/VIBRANT |
| 6.54 | 43731 | 78 | `generax` | benoitmorel/generax |
| 6.53 | 22805 | 149 | `srst2` | katholt/srst2 |
| 6.53 | 22134 | 152 | `fusioncatcher` | ndaniel/fusioncatcher |
| 6.52 | 22411 | 147 | `seqprep` | jstjohn/SeqPrep |
| 6.52 | 36724 | 89 | `goalign` | fredericlemoine/goalign |
| 6.51 | 35732 | 89 | `phyloflash` | HRGV/phyloFlash |
| 6.50 | 39804 | 79 | `variantbam` | jwalabroad/VariantBam |
| 6.50 | 17329 | 182 | `cramino` | wdecoster/cramino |

### Tier 5 — useful (6.0–6.5) — 49 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 6.49 | 33173 | 92 | `nanosv` | mroosmalen/nanosv |
| 6.49 | 20201 | 151 | `hybracter` | gbouras13/hybracter |
| 6.48 | 27899 | 108 | `isescan` | xiezhq/ISEScan |
| 6.46 | 28809 | 100 | `bcalm` | GATB/bcalm |
| 6.46 | 53648 | 53 | `samclip` | tseemann/samclip |
| 6.44 | 32638 | 83 | `cellsnp-lite` | single-cell-genetics/cellSNP |
| 6.44 | 2740517 | -1 | `last` | - |
| 6.43 | 21914 | 123 | `fastq-tools` | dcjones/fastq-tools |
| 6.42 | 23047 | 113 | `rgt` | CostaLab/reg-gen |
| 6.39 | 10445 | 235 | `cnvnator` | abyzovlab/CNVnator |
| 6.39 | 9950 | 243 | `nextpolish` | Nextomics/NextPolish |
| 6.38 | 24165 | 99 | `shapeit4` | odelaneau/shapeit4 |
| 6.36 | 65971 | 34 | `sistr_cmd` | phac-nml/sistr_cmd |
| 6.35 | 18211 | 121 | `ribodetector` | hzi-bifo/RiboDetector |
| 6.35 | 25462 | 86 | `plassembler` | gbouras13/plassembler |
| 6.34 | 7891 | 278 | `parasail` | jeffdaily/parasail |
| 6.34 | 48410 | 44 | `desalt` | ydLiu-HIT/deSALT |
| 6.33 | 19698 | 108 | `graphlan` | biobakery/graphlan |
| 6.32 | 14982 | 139 | `fqtools` | alastair-droop/fqtools |
| 6.31 | 26075 | 78 | `ntcard` | bcgsc/ntCard |
| 6.31 | 28804 | 70 | `snap` | KorfLab/SNAP |
| 6.30 | 24282 | 81 | `flexbar` | seqan/flexbar |
| 6.27 | 58537 | 31 | `binsanity` | edgraham/BinSanity |
| 6.25 | 12239 | 143 | `faststructure` | rajanil/fastStructure |
| 6.24 | 6302 | 272 | `foldmason` | steineggerlab/foldmason |
| 6.23 | 10660 | 160 | `defense-finder` | mdmparis/defense-finder |
| 6.23 | 33043 | 50 | `prodigal-gv` | apcamargo/prodigal-gv |
| 6.22 | 41668 | 39 | `hicstuff` | koszullab/hicstuff |
| 6.20 | 61397 | 25 | `confindr` | lowandrew/ConFindr |
| 6.19 | 15848 | 97 | `ea-utils` | ExpressionAnalysis/ea-utils |
| 6.18 | 6597 | 229 | `autocycler` | rrwick/Autocycler |
| 6.18 | 20825 | 71 | `tracer` | beast-dev/tracer |
| 6.17 | 6811 | 218 | `lexicmap` | shenwei356/LexicMap |
| 6.16 | 27853 | 51 | `sequencetools` | stschiff/sequenceTools |
| 6.16 | 16255 | 87 | `integron_finder` | gem-pasteur/Integron_Finder |
| 6.15 | 37138 | 37 | `frogs` | geraldinepascal/FROGS |
| 6.15 | 39084 | 35 | `makehub` | Gaius-Augustus/MakeHub |
| 6.14 | 14744 | 92 | `cuttlefish` | COMBINE-lab/cuttlefish |
| 6.11 | 22016 | 58 | `magpurify` | snayfach/MAGpurify |
| 6.06 | 7237 | 158 | `phold` | gbouras13/phold |
| 6.06 | 13998 | 81 | `panacota` | gem-pasteur/PanACoTA |
| 6.05 | 29629 | 37 | `gfaffix` | marschall-lab/gfaffix |
| 6.05 | 11540 | 96 | `treecluster` | niemasd/TreeCluster |
| 6.04 | 21593 | 50 | `varvamp` | jonas-fuchs/varVAMP |
| 6.04 | 13901 | 77 | `macsyfinder` | gem-pasteur/macsyfinder |
| 6.02 | 34080 | 30 | `ultraplex` | ulelab/ultraplex |
| 6.02 | 17532 | 59 | `porechop_abi` | bonsai-team/Porechop_ABI |
| 6.02 | 11912 | 86 | `squeakr` | splatlab/squeakr |
| 6.01 | 16470 | 61 | `swipe` | torognes/swipe |

### Tier 6 — long tail (< 6.0) — 207 tools

| score | downloads | stars | tool | github |
|------:|----------:|------:|------|--------|
| 5.99 | 9846 | 98 | `rfmix` | slowkoni/rfmix |
| 5.97 | 13000 | 71 | `homopolish` | ythuang0522/homopolish |
| 5.92 | 118880 | 6 | `mikado` | lucventurini/mikado |
| 5.92 | 10110 | 81 | `minipolish` | rrwick/Minipolish |
| 5.91 | 12080 | 67 | `cath-tools` | UCLOrengoGroup/cath-tools |
| 5.91 | 5807 | 139 | `vcf-validator` | EBIVariation/vcf-validator |
| 5.91 | 22565 | 35 | `nanomotif` | MicrobialDarkMatter/nanomotif |
| 5.90 | 11810 | 67 | `ska` | simonrharris/SKA |
| 5.87 | 11428 | 64 | `oases` | dzerbino/oases |
| 5.85 | 19528 | 35 | `pullseq` | bcthomas/pullseq |
| 5.84 | 16082 | 42 | `twopaco` | medvedevgroup/TwoPaCo |
| 5.82 | 28634 | 22 | `quicktree` | khowe/quicktree |
| 5.80 | 25210 | 24 | `fastqsplitter` | LUMC/fastqsplitter |
| 5.80 | 12289 | 50 | `rfplasmid` | aldertzomer/RFPlasmid |
| 5.78 | 5891 | 102 | `shapeit5` | odelaneau/shapeit5 |
| 5.77 | 24762 | 23 | `orfm` | wwood/OrfM |
| 5.76 | 4709 | 120 | `pandora` | rmcolq/pandora |
| 5.75 | 37510 | 14 | `genomethreader` | genometools/genomethreader |
| 5.74 | 20433 | 26 | `sword` | rvaser/sword |
| 5.72 | 27912 | 18 | `rapidnj` | somme89/rapidNJ |
| 5.72 | 13145 | 39 | `pastml` | evolbioinfo/pastml |
| 5.72 | 20085 | 25 | `sicer2` | zanglab/SICER2 |
| 5.70 | 8307 | 59 | `popscle` | statgen/popscle |
| 5.68 | 481878 | -1 | `gmap` | - |
| 5.68 | 5513 | 86 | `lrge` | mbhall88/lrge |
| 5.66 | 32817 | 13 | `hclust2` | SegataLab/hclust2 |
| 5.66 | 3109 | 146 | `myloasm` | bluenote-1577/myloasm |
| 5.65 | 11413 | 38 | `emirge` | csmiller/EMIRGE |
| 5.65 | 12000 | 36 | `ale` | sc932/ALE |
| 5.63 | 10609 | 39 | `taxadb` | HadrienG/taxadb |
| 5.63 | 422951 | -1 | `clustalw` | - |
| 5.61 | 4620 | 87 | `grapetree` | achtman-lab/GrapeTree |
| 5.57 | 16304 | 22 | `msamtools` | arumugamlab/msamtools |
| 5.55 | 4077 | 87 | `kmtricks` | tlemane/kmtricks |
| 5.55 | 19759 | 17 | `hops` | rhuebler/HOPS |
| 5.54 | 4200 | 81 | `coolpuppy` | open2c/coolpuppy |
| 5.54 | 6467 | 52 | `clinker` | Oshlack/Clinker |
| 5.53 | 84299 | 3 | `sap` | mathbio-nimr-mrc-ac-uk/SAP |
| 5.53 | 3989 | 83 | `quip` | dcjones/quip |
| 5.52 | 20809 | 15 | `shigatyper` | CFSAN-Biostatistics/shigatyper |
| 5.51 | 12067 | 26 | `plascope` | GuilhemRoyer/PlaScope |
| 5.51 | 10815 | 29 | `cgmlst-dists` | tseemann/cgmlst-dists |
| 5.50 | 5710 | 54 | `kmerstream` | pmelsted/KmerStream |
| 5.47 | 297688 | -1 | `megahit` | voutcn/megah |
| 5.47 | 3853 | 75 | `viralverify` | ablab/viralVerify |
| 5.46 | 288545 | -1 | `gromacs` | - |
| 5.45 | 2548 | 109 | `mummer2circos` | metagenlab/mummer2circos |
| 5.42 | 263000 | -1 | `kma` | - |
| 5.41 | 2792 | 92 | `omark` | DessimozLab/omark |
| 5.41 | 254789 | -1 | `circos` | - |
| 5.40 | 250821 | -1 | `mlst` | tseemann/mls |
| 5.39 | 247598 | -1 | `emboss` | - |
| 5.38 | 15090 | 15 | `bamm` | Ecogenomics/BamM |
| 5.38 | 2965 | 80 | `reseek` | rcedgar/reseek |
| 5.38 | 11402 | 20 | `viromeqc` | SegataLab/viromeqc |
| 5.37 | 13723 | 16 | `unitig-counter` | johnlees/unitig-counter |
| 5.36 | 16515 | 13 | `shigeifinder` | LanLab/ShigEiFinder |
| 5.36 | 4591 | 49 | `grenedalf` | lczech/grenedalf |
| 5.36 | 228097 | -1 | `qualimap` | - |
| 5.35 | 225982 | -1 | `nanoplot` | wdecoster/NanoPlo |
| 5.35 | 5874 | 37 | `scapp` | Shamir-Lab/SCAPP |
| 5.35 | 223061 | -1 | `glimmerhmm` | - |
| 5.34 | 2766 | 78 | `catfasta2phyml` | nylander/catfasta2phyml |
| 5.32 | 211097 | -1 | `rgi` | arpcard/r |
| 5.32 | 136 | 1539 | `test` | lh3/seqtk |
| 5.28 | 190635 | -1 | `biom-format` | - |
| 5.27 | 1880 | 98 | `sshash` | jermp/sshash |
| 5.24 | 2146 | 80 | `dna-nn` | lh3/dna-nn |
| 5.24 | 2496 | 68 | `msmc2` | stschiff/msmc2 |
| 5.23 | 6468 | 25 | `mdmcleaner` | KIT-IBG-5/mdmcleaner |
| 5.21 | 7417 | 21 | `squirrel` | aineniamh/squirrel |
| 5.21 | 2709 | 59 | `phynteny` | susiegriggo/Phynteny |
| 5.20 | 157143 | -1 | `plink` | - |
| 5.18 | 149839 | -1 | `mageck` | - |
| 5.17 | 8724 | 16 | `msweep` | PROBIC/mSWEEP |
| 5.16 | 144732 | -1 | `taxonkit` | shenwei356/taxonk |
| 5.15 | 3751 | 37 | `snaptools` | r3fang/SnapTools |
| 5.14 | 34827 | 3 | `ggcaller` | samhorsfield96/ggCaller |
| 5.14 | 670 | 204 | `souporcell` | wheaton5/souporcell |
| 5.14 | 137423 | -1 | `vcontact2` | - |
| 5.13 | 135293 | -1 | `poa` | - |
| 5.10 | 3719 | 33 | `proovframe` | thackl/proovframe |
| 5.07 | 117601 | -1 | `rnastructure` | - |
| 5.06 | 8927 | 12 | `genometools` | flo-compbio/genometools |
| 5.03 | 107997 | -1 | `phylip` | - |
| 5.03 | 107061 | -1 | `vg` | vgteam/v |
| 5.03 | 2183 | 48 | `kmindex` | tlemane/kmindex |
| 5.03 | 6667 | 15 | `taxator-tk` | fungs/taxator-tk |
| 5.02 | 3202 | 32 | `ancestry_hmm` | russcd/Ancestry_HMM |
| 5.00 | 99145 | -1 | `maker` | - |
| 4.99 | 98759 | -1 | `raxml-ng` | amkozlov/raxml-n |
| 4.98 | 96501 | -1 | `exonerate` | - |
| 4.97 | 94187 | -1 | `igblast` | - |
| 4.96 | 90724 | -1 | `nanofilt` | wdecoster/nanofil |
| 4.96 | 90369 | -1 | `chromosight` | koszullab/chromosigh |
| 4.95 | 7401 | 11 | `malder` | joepickrell/malder |
| 4.94 | 86232 | -1 | `mustang` | - |
| 4.93 | 85594 | -1 | `dialign-tx` | - |
| 4.93 | 84316 | -1 | `probconsrna` | - |
| 4.92 | 84096 | -1 | `cufflinks` | - |
| 4.92 | 83296 | -1 | `probcons` | - |
| 4.92 | 1353 | 60 | `fulgor` | jermp/fulgor |
| 4.90 | 79136 | -1 | `fastx_toolkit` | agordon/fastx_toolk |
| 4.88 | 75889 | -1 | `epa-ng` | Pbdas/epa-n |
| 4.87 | 2563 | 28 | `metator` | koszullab/metator |
| 4.87 | 73720 | -1 | `odgi` | pangenome/od |
| 4.86 | 72321 | -1 | `tophat` | infphilo/topha |
| 4.86 | 4515 | 15 | `mgems` | PROBIC/mGEMS |
| 4.83 | 2571 | 25 | `bamstats` | guigolab/bamstats |
| 4.82 | 65468 | -1 | `fraggenescan` | - |
| 4.81 | 65236 | -1 | `velvet` | dzerbino/velve |
| 4.81 | 2243 | 28 | `phylodeep` | evolbioinfo/phylodeep |
| 4.76 | 57779 | -1 | `fastme` | - |
| 4.72 | 711 | 73 | `padloc` | padlocbio/padloc |
| 4.72 | 51972 | -1 | `checkv` | - |
| 4.71 | 51845 | -1 | `angsd` | - |
| 4.71 | 51783 | -1 | `filtlong` | rrwick/Filtlon |
| 4.70 | 49812 | -1 | `skani` | bluenote-1577/skan |
| 4.69 | 7052 | 6 | `consel` | shimo-lab/consel |
| 4.69 | 49238 | -1 | `express` | - |
| 4.69 | 48492 | -1 | `clipkit` | jlsteenwyk/clipk |
| 4.68 | 47785 | -1 | `proda` | - |
| 4.67 | 46874 | -1 | `pyani` | widdowquinn/pyan |
| 4.65 | 45105 | -1 | `srprism` | - |
| 4.64 | 43293 | -1 | `beagle` | - |
| 4.63 | 43042 | -1 | `blasr` | PacificBiosciences/blasr |
| 4.63 | 42200 | -1 | `prinseq` | - |
| 4.60 | 669 | 59 | `psipred` | psipred/psipred |
| 4.60 | 40000 | -1 | `ska2` | bacpop/ska.rus |
| 4.60 | 39553 | -1 | `repeatscout` | Dfam-consortium/RepeatScou |
| 4.58 | 38024 | -1 | `flash` | - |
| 4.57 | 37349 | -1 | `pear` | - |
| 4.57 | 2164 | 16 | `amiga` | firasmidani/amiga |
| 4.56 | 35900 | -1 | `bifrost` | pmelsted/bifros |
| 4.55 | 35705 | -1 | `squizz` | - |
| 4.52 | 32922 | -1 | `dashing` | dnbaker/dashin |
| 4.48 | 30234 | -1 | `smoothxg` | pangenome/smoothx |
| 4.48 | 29963 | -1 | `openbabel` | - |
| 4.47 | 893 | 32 | `pyani-plus` | pyani-plus/pyani-plus |
| 4.45 | 4698 | 5 | `architeuthis` | cdiener/architeuthis |
| 4.41 | 25965 | -1 | `malt` | - |
| 4.39 | 24580 | -1 | `datamash` | - |
| 4.37 | 23494 | -1 | `vmatch` | - |
| 4.34 | 21923 | -1 | `treemix` | - |
| 4.33 | 21494 | -1 | `modeltest-ng` | ddarriba/modeltes |
| 4.32 | 20932 | -1 | `itsx` | - |
| 4.28 | 18874 | -1 | `phipack` | - |
| 4.27 | 18831 | -1 | `iphop` | - |
| 4.27 | 18702 | -1 | `magicblast` | - |
| 4.26 | 18331 | -1 | `gblocks` | - |
| 4.24 | 17439 | -1 | `plasmidfinder` | - |
| 4.22 | 16612 | -1 | `lordec` | - |
| 4.22 | 16423 | -1 | `pal2nal` | - |
| 4.22 | 16416 | -1 | `ezclermont` | nickp60/barrnap-python |
| 4.21 | 16337 | -1 | `libsvm` | - |
| 4.18 | 15114 | -1 | `mauvealigner` | - |
| 4.17 | 14655 | -1 | `amos` | - |
| 4.16 | 14532 | -1 | `pbalign` | PacificBiosciences/pbalign |
| 4.15 | 1289 | 10 | `shigapass` | imanyass/ShigaPass |
| 4.14 | 13834 | -1 | `rdp_classifier` | - |
| 4.11 | 445 | 28 | `cayman` | zellerlab/cayman |
| 4.10 | 12626 | -1 | `gcta` | - |
| 4.09 | 12261 | -1 | `deepsig` | BolognaBiocomp/deeps |
| 4.08 | 12082 | 0 | `slamem` | sguizard/slaMEM |
| 4.06 | 11455 | -1 | `pbwt` | richarddurbin/pbw |
| 4.05 | 11263 | -1 | `resfinder` | - |
| 4.03 | 10597 | -1 | `smina` | - |
| 4.00 | 10077 | -1 | `proteowizard` | - |
| 3.98 | 9525 | -1 | `codonw` | - |
| 3.98 | 9513 | -1 | `finestructure` | - |
| 3.96 | 9177 | -1 | `3seq` | - |
| 3.95 | 8918 | -1 | `ghostx` | - |
| 3.88 | 7580 | -1 | `alder` | - |
| 3.88 | 7526 | -1 | `bamkit` | hall-lab/bamk |
| 3.87 | 7397 | -1 | `make_prg` | rmcolq/make_pr |
| 3.86 | 7263 | -1 | `reaper` | - |
| 3.85 | 7089 | -1 | `ceas` | - |
| 3.84 | 6943 | -1 | `req` | - |
| 3.83 | 6687 | -1 | `fsa` | - |
| 3.82 | 6536 | -1 | `realphy` | - |
| 3.81 | 6466 | -1 | `fqzcomp` | - |
| 3.81 | 6450 | -1 | `rust-mdbg` | ekimb/rust-mdb |
| 3.78 | 6014 | -1 | `msaprobs` | - |
| 3.77 | 5940 | -1 | `shapemapper` | - |
| 3.77 | 5843 | 0 | `amap` | mes5k/amap-align |
| 3.77 | 5820 | -1 | `bmge` | - |
| 3.75 | 5643 | -1 | `jvarkit` | lindenb/jvark |
| 3.71 | 5072 | -1 | `sonneityping` | katholt/sonneitypin |
| 3.70 | 4976 | -1 | `clusterone` | - |
| 3.69 | 4878 | -1 | `pycrac` | - |
| 3.68 | 4807 | -1 | `serotypefinder` | - |
| 3.60 | 4024 | -1 | `virulencefinder` | - |
| 3.60 | 4019 | -1 | `fastml` | - |
| 3.60 | 3963 | -1 | `baypass` | - |
| 3.60 | 3962 | -1 | `pod5` | nanoporetech/pod5-file-forma |
| 3.57 | 3675 | -1 | `ratt` | ThomasDOtto/ra |
| 3.45 | 2840 | -1 | `kmerfinder` | - |
| 3.45 | 2806 | -1 | `rock` | - |
| 3.42 | 2632 | -1 | `provean` | - |
| 3.41 | 2596 | -1 | `fastsimcoal2` | - |
| 3.35 | 560 | 3 | `cactus-gfa-tools` | ComparativeGenomicsToolkit/cactus-gfa-tools |
| 3.26 | 45 | 39 | `alerax` | BenoitMorel/AleRax |
| 3.23 | 1694 | -1 | `pling` | iqbal-lab-org/plin |
| 3.22 | 1651 | -1 | `ggcat` | algbio/ggca |
| 3.19 | 1531 | -1 | `plasnet` | leoisl/plasne |
| 2.51 | 324 | -1 | `hal2vg` | ComparativeGenomicsToolkit/hal2v |
| 1.56 | 35 | 0 | `genescanner` | Sheppard-Lab/GeneScanner |

## Cleanup

Once this plan is committed, delete the scratch wishlist files: `TODO.single`, `TODO.single.sorted`, `TODO.single.cache.json`, `.TODO.single.swp`.


## Appendix — wishlist tools with NO Bioconda recipe (334 tools)

Excluded from the main plan (would need source / Docker builds). Lower priority; revisit individually. Preserved here so the original wishlist is not lost.

| tool | github |
|------|--------|
| `fasta` | fastapi/fastapi |
| `medi` | NanmiCoder/MediaCrawler |
| `SLiM` | slimtoolkit/slim |
| `alphafold` | google-deepmind/alphafold |
| `ANTs` | panjf2000/ants |
| `BEAM` | apache/beam |
| `ASSU` | rest-assured/rest-assured |
| `boltz` | jwohlwend/boltz |
| `lammps` | lammps/lammps |
| `bmtools` | OpenBMB/BMTools |
| `RoseTTAFold` | RosettaCommons/RoseTTAFold |
| `ELP` | jorgenschaefer/elpy |
| `blast+` | julianshapiro/blast |
| `mkl` | jamesnguyenhub/mkloader |
| `BindCraft` | martinpacesa/BindCraft |
| `autodock_vina` | ccsb-scripps/AutoDock-Vina |
| `ete` | etetoolkit/ete |
| `Meerkat` | HazyResearch/meerkat |
| `raven` | 0x09AL/raven |
| `fmriprep` | nipreps/fmriprep |
| `rosetta` | LatticeX-Foundation/Rosetta |
| `RFantibody` | RosettaCommons/RFantibody |
| `fpocket` | Discngine/fpocket |
| `atac-seq-pipeline` | ENCODE-DCC/atac-seq-pipeline |
| `signalp` | SignalPilot-Labs/SignalPilot |
| `RoseTTAFold2NA` | uw-ipd/RoseTTAFold2NA |
| `EmPATHi` | lukeed/empathic |
| `APS` | MPSU/APS |
| `AlphaPulldown` | KosinskiLab/AlphaPulldown |
| `SHRiMP` | adjust/shrimp |
| `modkit` | nanoporetech/modkit |
| `beast-mcmc` | beast-dev/beast-mcmc |
| `AFNI` | afni/afni |
| `mob-suite` | phac-nml/mob-suite |
| `EMAN2` | cryoem/eman2 |
| `MESSI` | marcosesperon/Messi |
| `MGEfinder` | bhattlab/MGEfinder |
| `RNA_Bloom` | BirolLab/RNA-Bloom |
| `SARTools` | PF2-pasteur-fr/SARTools |
| `kofam_scan` | takaram/kofam_scan |
| `membrain-seg` | teamtomo/membrain-seg |
| `fastq_screen` | StevenWingett/FastQ-Screen |
| `Scipion` | I2PC/scipion |
| `SLiPP` | javajigi/slipp |
| `silent_tools` | bcov77/silent_tools |
| `AreTomo` | czimaginginstitute/AreTomo2 |
| `MicrobeMod` | cultivarium/MicrobeMod |
| `rsat` | ropensci/rsat |
| `shapeit` | Appfairy/shapeit |
| `AreTomo3` | czimaginginstitute/AreTomo3 |
| `mapDamage` | ginolhac/mapDamage |
| `Bactabolize` | kelwyres/Bactabolize |
| `ReporTree` | insapathogenomics/ReporTree |
| `kmdiff` | tlemane/kmdiff |
| `BioPathNet` | emyyue/BioPathNet |
| `LS_BSR` | jasonsahl/LS-BSR |
| `FANTASIA` | amfauzn/Fantasia |
| `lsd2` | tothuhien/lsd2 |
| `MHC_I` | 2308087369/mHC-iTransformer |
| `louvain` | qq547276542/Louvain |
| `bam2fastq` | jts/bam2fastq |
| `LINtree` | PatchMon/lintree |
| `bactsnp` | IEkAdN/BactSNP |
| `MITE-Tracker` | INTABiotechMJ/MITE-Tracker |
| `micca` | compmetagen/micca |
| `Reapr` | ted-xie/REAPR |
| `fastq_info` | raymondkiu/fastq-info |
| `fatools` | trmznt/fatools |
| `miteFinder` | jhu99/miteFinder |
| `BioEM` | bio-phys/BioEM |
| `fastGlobeTrotter` | hellenthal-group-UCL/fastGLOBETROTTER |
| `rmsFinder` | liampshaw/rmsFinder |
| `fastGEAR` | PiterYang/fastgear |
| `MADroot` | davidjamesbryant/MADroot |
| `extract_genes_ABRIcate` | boasvdp/extract_genes_ABRicate |
| `fivepseq` | lilit-nersisyan/fivepseq |
| `MetaBAT` | marcinn/metabat |
| `registre` | GovernIB/registre |
| `ResMap` | akucukelbir/resmap |
| `silix` | philberty/silix |
| `SMRT-Link` | WenchaoLin/SMRT-Link |
| `annovar` | bioinfo-chru-strasbourg/annovar |
| `EMReady` | huang-laboratory/EMReady |
| `kmer-sets-compression` | kkty/kmer-sets-compression |
| `eFASTA` | C3BI-pasteur-fr/eFASTA |
| `SNP2HLA` | damiantarasek/snp2hla |
| `AlienDiscover` | lawrencefoo/AlienDiscoveryMission |
| `amrfinder` | CORRS-LAB/AMRfinder |
| `ANIcalculator` | linarus85/Anicalculator |
| `ASLES` | AsleshaMounika/AsleshaMounika |
| `BayesTraits` | ChrisOrgan/BayesTraits |
| `epi2me-wf-16s` | manualfaros/epi2me-wf-16s |
| `FASTA2AGP` | vesteinn/fasta2agp |
| `fastaextract` | C3BI-pasteur-fr/fastaextract |
| `FQreport` | jalexspringer/fqreport |
| `map2cov` | fsvieira/map2covjson |
| `MaxBin` | saviour29/maxbin |
| `minidna` | acorrenson/miniDna |
| `Salmonella-CRISPR-Typing` | C3BI-pasteur-fr/Salmonella-CRISPR-Typing |
| `sbgrid` | ShuaibSB/sbgrid |
| `AlienRemover` | — |
| `Assembly_Likelihood_Estimator` | — |
| `blastTaxoAnalysis` | — |
| `bppsuite` | — |
| `bsoft` | — |
| `BTyper` | — |
| `bwa_mem2` | — |
| `C2A.A2C` | — |
| `CAFE5` | — |
| `caller` | — |
| `capmq` | — |
| `CAT_pack` | — |
| `cdbfasta` | — |
| `cellpose` | — |
| `cellranger` | — |
| `cellranger-arc` | — |
| `cellranger-atac` | — |
| `Cenote-Taker2` | — |
| `cgatools` | — |
| `ChimeraX` | — |
| `chromopainter` | — |
| `cistem` | — |
| `CLASS2` | — |
| `clc-assembly-cell` | — |
| `CLCGenomicsWorkbench` | — |
| `ClinSV` | — |
| `Clustal-Omega` | — |
| `Colate` | — |
| `contig-extender` | — |
| `contig_info` | — |
| `Convert3D` | — |
| `COPLA` | — |
| `CoPro` | — |
| `CRISPRCasFinder` | — |
| `CRISPRcasIdentifier` | — |
| `CRISPRidentify` | — |
| `crop` | — |
| `cryoCARE` | — |
| `cryoSPARC` | — |
| `ctffind` | — |
| `DaliLite` | — |
| `dbgwas` | — |
| `dbtools` | — |
| `DeepETPicker` | — |
| `deeplocpro` | — |
| `DeepTMHMM` | — |
| `deformetrica` | — |
| `dfast_core` | — |
| `digIS` | — |
| `dorado` | — |
| `dssp` | — |
| `duplex_tools` | — |
| `Dynamo` | — |
| `EBG` | — |
| `ecoli_serotyping` | — |
| `edirect` | — |
| `epi2me-wf-alignment` | — |
| `epi2me-wf-bacterial-genomes` | — |
| `epi2me-wf-human-variation` | — |
| `epi2me-wf-metagenomics` | — |
| `epi2me-wf-single-cell` | — |
| `fq2dna` | — |
| `fqCleanER` | — |
| `FQsum` | — |
| `freec` | — |
| `freesurfer` | — |
| `FSL` | — |
| `FUNGuild` | — |
| `gbk2ENA` | — |
| `gbwtgraph` | — |
| `Gctf` | — |
| `gemmi` | — |
| `GemSIM` | — |
| `genemark` | — |
| `genemark-es` | — |
| `GenomeAnalysisTK` | — |
| `GenomeSPOT` | — |
| `getphylo` | — |
| `gingr` | — |
| `GLIMPSE` | — |
| `gnina` | — |
| `gnomix` | — |
| `golden` | — |
| `gplas2` | — |
| `GraphChainer` | — |
| `GRM-MAF-LD` | — |
| `growthpred` | — |
| `GUSHR` | — |
| `gutsmash` | — |
| `haddock3` | — |
| `hal` | — |
| `harvest-tools` | — |
| `HGTector` | — |
| `HiC-Pro` | — |
| `hifix` | — |
| `hlahd` | — |
| `hmmtop` | — |
| `html4blast` | — |
| `IMOD` | — |
| `IMP` | — |
| `IQ-TREE` | — |
| `IS_mapper` | — |
| `IsoNet` | — |
| `JAGS` | — |
| `jmodeltest2` | — |
| `juicer` | — |
| `Jupyter-Notebook` | — |
| `KaKs_Calculator` | — |
| `Kalign` | — |
| `KaMRaT` | — |
| `MetaGeneAnnotator` | — |
| `mfold_util` | — |
| `MotionCor2` | — |
| `MotionCor3` | — |
| `msa` | — |
| `MSMC_IM` | — |
| `MSTclust` | — |
| `MToolBox` | — |
| `musket` | — |
| `muTect` | — |
| `MutTui` | — |
| `NAMD` | — |
| `nanodna` | — |
| `nauty` | — |
| `ncbi-datasets` | — |
| `ncbitools` | — |
| `ncoils` | — |
| `netMHCpan` | — |
| `networkanalysis` | — |
| `newick-utils` | — |
| `NiftyMIC` | — |
| `Noisy` | — |
| `OGRI` | — |
| `ohana` | — |
| `OMA` | — |
| `ont-guppy` | — |
| `openfold` | — |
| `oriTfinder` | — |
| `orthosnap` | — |
| `OSNAp` | — |
| `Parabricks` | — |
| `Paratype` | — |
| `PathogenFinder2` | — |
| `pcma` | — |
| `pdb_tools` | — |
| `PEET` | — |
| `penncnv` | — |
| `PGAP` | — |
| `PhageTerm` | — |
| `phammseqs` | — |
| `PhaseFinder` | — |
| `phobius` | — |
| `phrap` | — |
| `phylobayes` | — |
| `phyml-sms` | — |
| `picard-tools` | — |
| `pixy` | — |
| `plasmidEC` | — |
| `PlasX` | — |
| `plumed` | — |
| `pointfinder` | — |
| `PoPoolationTE2` | — |
| `PRISM` | — |
| `ProteinMPNN` | — |
| `ProtTest` | — |
| `PROVEAN-Assembly-Line` | — |
| `pseudofinder` | — |
| `ptools` | — |
| `pyem` | — |
| `PyPythia` | — |
| `qaf_demux` | — |
| `qiime2` | — |
| `qsimscan` | — |
| `RaFAH` | — |
| `rainbowfish` | — |
| `RAiSD` | — |
| `remove_duplicates_from_sorted_fastq` | — |
| `RepeatAnalysisTools` | — |
| `rmblastn` | — |
| `SAM2MSA` | — |
| `sbgrid.ORIG` | — |
| `SNPPar` | — |
| `soap` | — |
| `SOAPindel` | — |
| `spaceranger` | — |
| `SparsePainter` | — |
| `spIsoNet` | — |
| `splitpipe` | — |
| `sprime` | — |
| `SQANTI3` | — |
| `sra_sdk` | — |
| `ssaha2` | — |
| `stampy` | — |
| `Superfold` | — |
| `SVRTK` | — |
| `SweeD` | — |
| `SynTViewTools` | — |
| `tama` | — |
| `taxodb_ncbi` | — |
| `taxoptimizer` | — |
| `taxo_rrna` | — |
| `tcoffee` | — |
| `TemStaPro` | — |
| `testnh` | — |
| `texlive` | — |
| `themisto` | — |
| `TIP_finder` | — |
| `TM-align` | — |
| `tmhmm` | — |
| `TNT` | — |
| `topaz` | — |
| `tRAX` | — |
| `tree-puzzle` | — |
| `TrimGalore` | — |
| `trinityrnaseq` | — |
| `trnascan` | — |
| `TWL_NINJA` | — |
| `uBin` | — |
| `UCSC-tools` | — |
| `UMI-tools` | — |
| `unafold` | — |
| `vcf2mst` | — |
| `viga` | — |
| `ViPTreeGen` | — |
| `viralComplete` | — |
| `VIRIDIC` | — |
| `VirVarSeq` | — |
| `VPhaser-2` | — |
| `warp` | — |
| `WIsH` | — |
| `witchi` | — |
| `wtdbg2` | — |
| `xeniumranger` | — |
| `xxr` | — |

