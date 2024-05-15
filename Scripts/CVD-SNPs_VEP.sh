#!/bin/bash
#SBATCH --partition=X
#SBATCH --requeue 
#SBATCH --job-name=X
#SBATCH --nodes=X
#SBATCH --ntasks=X
#SBATCH --cpus-per-task=X
#SBATCH --mem=X
#SBATCH --time=X
#SBATCH --output=/PATH/CVD-SNPs_VEP.%N.%j.olog
#SBATCH --error=/PATH/CVD-SNPs_VEP.%N.%j.elog
#SBATCH --mail-type=BEGIN,END,FAIL

cd /PATH/
module purge
source ~/.bashrc
conda activate Ensembl-VEP

rm CVD-SNPs_VEP_annotated.vcf
rm CVD-SNPs_VEP_annotated.vcf_summary.html
rm CVD-SNPs_VEP_filtered.vcf.gz

echo "Filtering VCFs..."
bcftools filter -R /PATH/Genes_CIGT.bed CVD-SNPs_VEP.vcf.gz -Oz -o CVD-SNPs_VEP_filtered.vcf.gz
if [ $? -ne 0 ]; then
    echo "bcftools FAILED!"
    exit 1
fi

# CADD
CADD_FILE="/PATH/whole_genome_SNVs.tsv.gz"
if [ ! -f "$CADD_FILE" ]; then
   echo "CADD NOT FOUND! Downloading..."
   wget -c https://krishna.gs.washington.edu/download/CADD/v1.7/GRCh38/whole_genome_SNVs.tsv.gz -O $CADD_FILE
fi

if [ ! -f "${CADD_FILE}.tbi" ]; then
    echo "Indexing $CADD_FILE..."
    tabix -p vcf "$CADD_FILE"
fi

echo "CADD PREPARED!"

# ClinVar
CLINVAR_FILE="/PATH/clinvar.vcf.gz"
if [ ! -f "$CLINVAR_FILE" ]; then
    echo "CLINVAR NOT FOUND! Exiting..."
    exit 1 
else
    if [ ! -f "${CLINVAR_FILE}.tbi" ]; then
        echo "Indexing $CLINVAR_FILE..."
        tabix -p vcf "$CLINVAR_FILE"
    fi
fi

echo "CLINVAR PREPARED!"

echo "VEP..."
# VEP
vep --input_file CVD-SNPs_VEP_filtered.vcf.gz --output_file CVD-SNPs_VEP_annotated.vcf --offline --cache \
    --vcf --species homo_sapiens --assembly GRCh38 \
    --dir_cache /PATH/Ensembl-VEP_cache \
    --dir_plugins /PATH/Ensembl-VEP/share/Plugins \
    --plugin CADD,/PATH/whole_genome_SNVs.tsv.gz \
    --af_gnomad \
    --custom /PATH/clinvar.vcf.gz,ClinVar,vcf,exact,0,CLNSIG,CLNREVSTAT,CLNDN \