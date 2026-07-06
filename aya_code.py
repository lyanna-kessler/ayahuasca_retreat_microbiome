# Lyanna Kessler
# 4/17/23
# Code and instructions for processing 16S Miseq data

''' 
Connect to lowry lab server:
smb://<IDK username>@ucbfiles.colorado.edu/IPHY/LowryLab

Download 1312023_Dawud_Kessler... folder with data
'''

# make an environment:
"""
Go to install QIIME page and it teaches you how to make a conda environment

"""

# conda activate /opt/anaconda3/envs/qiime2-2023.2

'''
! mkdir raw_sequences
! mv Undetermined* raw_sequences
%cd raw_sequences

! mv Undetermined_S0_L001_I1_001.fastq.gz barcodes.fastq.gz
! mv Undetermined_S0_L001_R1_001.fastq.gz forward.fastq.gz
! mv Undetermined_S0_L001_R2_001.fastq.gz reverse.fastq.gz
%cd ..


qiime tools import \
--type EMPPairedEndSequences \
--input-path raw_sequences \
--output-path paired-end-sequences.qza
'''

'''
# this takes awhile
qiime demux emp-paired \
--m-barcodes-file aya_meta.tsv \
--m-barcodes-column Barcodes \
--i-seqs paired-end-sequences.qza \
--p-rev-comp-barcodes \
--p-rev-comp-mapping-barcodes \
--output-dir demux 

qiime demux summarize \
--i-data demux/per_sample_sequences.qza \
--o-visualization demux/demux.qzv
'''

# go to qiime viewer website and view demux.qzv
# median: 36 quality score
# minimum length is 151


'''
# this one takes awhile
# trim barcodes up to 19-20
# trim 150 instead of 151 since read 151 has low quality
qiime dada2 denoise-paired \
--i-demultiplexed-seqs demux/per_sample_sequences.qza \
--p-trunc-len-f 150 \
--p-trunc-len-r 150 \
--p-trim-left-f 20 \
--p-trim-left-r 20 \
--output-dir dada2-results/

qiime feature-table summarize \
--i-table dada2-results/table.qza \
--o-visualization dada2-results/table.qzv \
--m-sample-metadata-file aya_meta.tsv
'''

# shortest read: 18796, sample 5819-2
# second shortest: 21544, sample 18-T2
# longest read: 67677, sample 25-T2

'''
# this one also takes awhile (longest one)
# download database first
qiime fragment-insertion sepp \
--i-representative-sequences dada2-results/representative_sequences.qza \
--i-reference-database sepp-refs-silva-128.qza \
--o-tree insertion-tree.qza \
--o-placements insertion-placements.qza

qiime fragment-insertion filter-features \
--i-table dada2-results/table.qza \
--i-tree insertion-tree.qza \
--o-filtered-table filtered-table.qza \
--o-removed-table removed-table.qza
'''

# the above was completed using fiji
# continuing the rest on this computer
'''
# download classifier before this
qiime feature-classifier classify-sklearn \
--i-reads dada2-out/representative_sequences.qza \
--i-classifier silva-138-99-515-806-nb-classifier.qza \
--output-dir silva-classified

qiime metadata tabulate \
--m-input-file silva-classified/classification.qza \
--o-visualization silva-classified/classification.qzv

mv silva-classified/classification.qza taxonomy-silva.qza
mv silva-classified/classification.qzv taxonomy-silva.qzv

qiime taxa filter-table \
  --i-table filtered-table.qza \
  --i-taxonomy taxonomy-silva.qza \
  --p-exclude mitochondria,chloroplast \
  --o-filtered-table noMito_noChloro-filtered-table.qza

qiime taxa barplot \
--i-table noMito_noChloro-filtered-table.qza \
--i-taxonomy taxonomy-silva.qza \
--m-metadata-file aya_meta.tsv \
--o-visualization taxa-barplot.qzv

'''

# FILTER TABLES TO ONLY KEEP IRB-Approved SAMPLES
# (and controls)

'''
qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta.tsv \
  --p-where  "[IRBapproved] IN ('yes','NA')"\
  --o-filtered-table ctrls-IRBapproved-filtered-table.qza 

qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta.tsv \
  --p-where "[IRBapproved]='yes'" \
  --o-filtered-table IRBapproved-filtered-table.qza 

qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta2.tsv \
  --o-filtered-table minimal-table.qza 

'''

# analysis

'''
qiime taxa barplot \
--i-table ctrls-IRBapproved-filtered-table.qza \
--i-taxonomy taxonomy-silva.qza \
--m-metadata-file aya_meta.tsv \
--o-visualization ci-taxa-barplot.qzv

qiime taxa barplot \
--i-table minimal-table.qza \
--i-taxonomy taxonomy-silva.qza \
--m-metadata-file aya_meta2.tsv \
--o-visualization minimal-barplot.qzv

# new metadata
qiime diversity core-metrics-phylogenetic \
  --i-phylogeny insertion-tree.qza \
  --i-table minimal-table.qza \
  --p-sampling-depth 18795 \
  --m-metadata-file aya_meta2.tsv \
  --output-dir core-diversity-results2

qiime diversity alpha-rarefaction \
  --i-table IRBapproved-filtered-table.qza \
  --i-phylogeny insertion-tree.qza \
  --p-max-depth 67677 \
  --o-visualization core-diversity-results/alpha-rarefaction.qzv

# NOT RUNNING
qiime diversity beta-rarefaction \
  --i-table IRBapproved-filtered-table.qza \
  --p-metric unweighted_unifrac \
  --p-clustering-method upgma \
  --m-metadata-file aya_meta2.tsv \
  --p-sampling-depth 67677 \
  --i-phylogeny insertion-tree.qza \
  --o-visualization core-diversity-results/beta-rarefaction.qzv


qiime diversity alpha-group-significance \
--i-alpha-diversity core-diversity-results/faith_pd_vector.qza \
--m-metadata-file aya_meta.tsv \
--o-visualization core-diversity-results/faith-pd-group-significance.qzv

qiime diversity alpha-correlation \
--i-alpha-diversity core-diversity-results/faith_pd_vector.qza \
--m-metadata-file aya_meta2.tsv \
--o-visualization core-diversity-results/faith-pd-correlation.qzv

qiime diversity beta-group-significance \
--i-distance-matrix core-diversity-results/unweighted_unifrac_distance_matrix.qza \
--m-metadata-file aya_meta2.tsv \
--m-metadata-column Timepoint_Type \
--o-visualization core-diversity-results/unweighted-unifrac-Timepoint_Type-significance.qzv \
--p-pairwise

# new analysis for only before/after samples
  qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results2/faith_pd_vector.qza \
  --m-metadata-file aya_meta2.tsv \
  --o-visualization core-diversity-results2/faith-pd-group-significance.qzv

  qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results2/faith_pd_vector.qza \
  --m-metadata-file aya_meta2.tsv \
  --o-visualization core-diversity-results2/faith-pd-correlation.qzv
  
  qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results2/shannon_vector.qza \
  --m-metadata-file aya_meta2.tsv \
  --o-visualization core-diversity-results2/shannon-significance.qzv

  qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results2/shannon_vector.qza \
  --m-metadata-file aya_meta2.tsv \
  --o-visualization core-diversity-results2/shannon-correlation.qzv

# METADATA Version 3
# new alpha for just samples (before/after) who consumed ayahuasca.
  qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-filtered-table meta3-table.qza 

  qiime taxa barplot \
  --i-table meta3-table.qza \
  --i-taxonomy taxonomy-silva.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization m3-barplot.qzv

  qiime diversity core-metrics-phylogenetic \
  --i-phylogeny insertion-tree.qza \
  --i-table meta3-table.qza \
  --p-sampling-depth 21543 \
  --m-metadata-file aya_meta3.tsv \
  --output-dir core-diversity-results3

  qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results3/faith_pd_vector.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization core-diversity-results3/faith-pd-group-significance.qzv

  qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results3/faith_pd_vector.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization core-diversity-results3/faith-pd-correlation.qzv
  
  qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results3/shannon_vector.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization core-diversity-results3/shannon-significance.qzv

  qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results3/shannon_vector.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization core-diversity-results3/shannon-correlation.qzv

  qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results3/evenness_vector.qza \
  --m-metadata-file aya_meta3.tsv \
  --o-visualization core-diversity-results3/evenness-significance.qzv

  qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results3/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta3.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results3/unweighted-significance.qzv \
  --p-pairwise

  qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results3/weighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta3.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results3/weighted-significance.qzv \
  --p-pairwise

'''

# subset data to only costa rica
# and subjects that did ayahuasca

'''
qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta_costarica.tsv \
    --p-where "[Consumed_Aya]='yes'" \
  --o-filtered-table cr-table.qza

qiime diversity core-metrics-phylogenetic \
  --i-phylogeny insertion-tree.qza \
  --i-table cr-table.qza \
  --p-sampling-depth 21543 \
  --m-metadata-file aya_meta_costarica.tsv \
  --output-dir core-diversity-results-cr

qiime diversity alpha-rarefaction \
  --i-table cr-table.qza \
  --i-phylogeny insertion-tree.qza \
  --p-max-depth 67677 \
  --o-visualization core-diversity-results-cr/alpha-rarefaction.qzv
  
qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr/faith_pd_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/faith-pd-group-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr/faith_pd_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/faith-pd-correlation.qzv
  
qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr/shannon_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/shannon-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr/shannon_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/shannon-correlation.qzv

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr/evenness_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/evenness-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr/evenness_vector.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --o-visualization core-diversity-results-cr/evenness-correlation.qzv
  
qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results-cr/unweighted-significance-timepoint.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --m-metadata-column Sex \
  --o-visualization core-diversity-results-cr/unweighted-significance-sex.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr/weighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results-cr/weighted-significance-timepoint.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr/weighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_costarica.tsv \
  --m-metadata-column Sex \
  --o-visualization core-diversity-results-cr/weighted-significance-sex.qzv \
  --p-pairwise

'''



# subset data to only costa rica
# and subjects that did ayahuasca
# REMOVE subject 17, missing psych metadata

'''
qiime feature-table filter-samples \
  --i-table noMito_noChloro-filtered-table.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --p-where "[Consumed_Aya]='yes'" \
  --o-filtered-table cr17-table.qza

qiime diversity core-metrics-phylogenetic \
  --i-phylogeny insertion-tree.qza \
  --i-table cr17-table.qza \
  --p-sampling-depth 21543 \
  --m-metadata-file aya_meta_cr-17.tsv \
  --output-dir core-diversity-results-cr17

qiime diversity alpha-rarefaction \
  --i-table cr17-table.qza \
  --i-phylogeny insertion-tree.qza \
  --p-max-depth 67677 \
  --o-visualization core-diversity-results-cr17/alpha-rarefaction.qzv
  
qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr17/faith_pd_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/faith-pd-group-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr17/faith_pd_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/faith-pd-correlation.qzv
  
qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr17/shannon_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/shannon-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr17/shannon_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/shannon-correlation.qzv

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-diversity-results-cr17/evenness_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/evenness-significance.qzv

qiime diversity alpha-correlation \
  --i-alpha-diversity core-diversity-results-cr17/evenness_vector.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --o-visualization core-diversity-results-cr17/evenness-correlation.qzv
  
qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr17/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results-cr17/unweighted-significance-timepoint.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr17/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --m-metadata-column Sex \
  --o-visualization core-diversity-results-cr17/unweighted-significance-sex.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr17/weighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_cr-1.tsv \
  --m-metadata-column Timepoint \
  --o-visualization core-diversity-results-cr17/weighted-significance-timepoint.qzv \
  --p-pairwise

qiime diversity beta-group-significance \
  --i-distance-matrix core-diversity-results-cr17/weighted_unifrac_distance_matrix.qza \
  --m-metadata-file aya_meta_cr-17.tsv \
  --m-metadata-column Sex \
  --o-visualization core-diversity-results-cr17/weighted-significance-sex.qzv \
  --p-pairwise

'''


# Running SCNIC

'''
qiime tools export 
--input-path cr-table.qza 
--output-path cr-table

conda activate SCNIC

SCNIC_analysis.py within -i cr-table/feature-table.biom -o within_output/ -m sparcc

SCNIC_analysis.py modules -i within_output/correls.txt -o modules_output/ --min_r .35 --table cr-table/feature-table.biom
'''

# get sequences

'''
qiime feature-table tabulate-seqs \
--i-data dada2-out/representative_sequences.qza \
--o-visualization dada2-out/rep_seqs.qzv

'''