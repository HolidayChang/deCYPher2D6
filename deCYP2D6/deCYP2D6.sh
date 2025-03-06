#!/bin/bash
#SBATCH -A MST109178       # Account name/project number
#SBATCH -J CYP2D6          # Job name
#SBATCH -p ngs1T_18        # Partition Name
#SBATCH -c 18              # Core preserved
#SBATCH --mem=1000G        # Memory used
#SBATCH -o out.log         # Path to the standard output file
#SBATCH -e err.log         # Path to the standard error output file
#SBATCH --mail-user=
#SBATCH --mail-type=FAIL,END

##############
# input data #
##############
sample=/staging/biology/u2499286/Assemblies/hg01258/assemblies/hg01258.paternal.f1_assembly_v2_genbank.fa.gz
samplename=HG01258P  
ref=/staging/biology/u2499286/deCYP2D6/CYP2D6.1.001.fa
haplo=/staging/biology/u2499286/deCYP2D6/CYP2D6.haplotypes_core.fasta
refseq_gene_core=/staging/biology/u2499286/deCYP2D6/RefSeqGeneCore



output_dir=/staging/biology/u2499286/deCYP2D6/${samplename}
mkdir -p ${output_dir} ${output_dir}/alignment ${output_dir}/extract ${output_dir}/result


export PATH=/staging/biology/u2499286/Assemblies/minimap2:$PATH
export PATH=/staging/biology/u2499286/Assemblies/deCYPher2D6/k8-0.2.4:$PATH

###############################
# Mapping reads with minimap2 #
###############################
minimap2 -cx splice:hq -G13k -y --cs -t32 -2 ${sample} ${ref} > ${output_dir}/alignment/mapping.paf

#############################
#      extract reads        #
#############################
python3 /staging/biology/u2499286/deCYP2D6/extract_loci_from_paf.py ${sample} ${output_dir}/alignment/mapping.paf ${output_dir}/extract/

echo "Extract reads: Finished"

##############################
# Sorting with minimap2 #
##############################

extract_dir=${output_dir}/extract


for fasta_file in ${extract_dir}/*.fasta
do
   
    filename=$(basename -- "$fasta_file")
    basename="${filename%.*}"

    
    minimap2 -cx splice:hq -G13k -y --cs -t32 -2 ${ref} "$fasta_file" | sort -k10,10n > "${extract_dir}/${basename}.paf"

    echo "Processing $fasta_file completed."
done

echo "Sorting Reads: Finished"
#############################
#      Variant calling      #
#############################

for paf_file in ${extract_dir}/*.paf
do
   
    filename2=$(basename -- "$paf_file")
    basename2="${filename2%.*}"

    
    k8-Linux /staging/biology/u2499286/Assemblies/minimap2/misc/paftools.js call -L3 -l3 -f ${ref} "$paf_file" > "${extract_dir}/${basename2}.vcf"

    echo "Variant Calling for $paf_file completed."
done

echo "Variant Calling: Finished"


##############################
#         Annotation         #
##############################

result_dir=${output_dir}/result


counter=1


for fasta_file in ${extract_dir}/*.fasta
do
    
    filename3="${result_dir}/comparison_${counter}.paf"

    
    minimap2 -cx splice:hq -G13k -y --cs -t32 -2 ${haplo} "$fasta_file" > "$filename3"


   
    counter=$((counter + 1))
done



counter=1


for vcf_file in ${extract_dir}/*.vcf
do
   
    filename4="${result_dir}/comparison_${counter}.txt"

   
    python3 /staging/biology/u2499286/deCYP2D6/anotation.py "$vcf_file" "$refseq_gene_core" "$filename4"

    
    counter=$((counter + 1))
done


echo "Annotating: Finished"

##############################
#      Comparison            #
##############################

counter=1
stop_processing=false

for comparison_file in ${result_dir}/comparison_*.txt
do
    
    paf_file="${result_dir}/comparison_${counter}.paf"
    
    
    allele_output="${result_dir}/allele_${counter}.txt"

    
    python3 /staging/biology/u2499286/deCYP2D6/comparison.py "$comparison_file" "$paf_file" "$allele_output"

    if grep -q '*5' "$allele_output"; then
        echo "*5 found in $allele_output. Stopping the process."
        stop_processing=true
        break
    fi

    
    counter=$((counter + 1))

   
    if $stop_processing; then
        break
    fi
done

echo "Job Finished"
