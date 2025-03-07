import os
import subprocess
import argparse
import pkg_resources
from deCYP2D6 import extract_loci_from_paf, anotation, comparison
def get_resource_path(resource_name):
    
    return pkg_resources.resource_filename('deCYP2D6', resource_name)

def run_command(command):
   
    print(f"Running: {command}")
    subprocess.run(command, shell=True, check=True)

def extract_loci_from_paf_script(fasta_file, paf_file, output_dir):
    
    command = [
        "python", get_resource_path("extract_loci_from_paf.py"),  # 調用腳本
        fasta_file,
        paf_file,
        output_dir
    ]
    subprocess.run(command, check=True)

def run_anotation_script(reference_vcf, compare_dir, output_file):
    
    command = [
        "python", get_resource_path("anotation.py"),  # 调用 annotation.py 脚本
        reference_vcf,
        compare_dir,
        output_file
    ]
    subprocess.run(command, check=True)

def run_comparison_script(txt_file, paf_file, output_file):
  
    command = [
        "python", get_resource_path("comparison.py"),  # 调用 annotation.py 脚本
        txt_file,
        paf_file,
        output_file
    ]
    subprocess.run(command, check=True)

def main():
    parser = argparse.ArgumentParser(description="CYP2D6 Analysis Pipeline")
    parser.add_argument("--sample", required=True, help="Path to the sample FASTA file")
    parser.add_argument("--samplename", required=True, help="Sample name (e.g., HG01258P)")
    parser.add_argument("--output", required=True, help="Output directory")
    
    args = parser.parse_args()

    sample = args.sample
    samplename = args.samplename
    output_dir = os.path.join(args.output, samplename)

    # 创建输出文件夹
    os.makedirs(f"{output_dir}/alignment", exist_ok=True)
    os.makedirs(f"{output_dir}/extract", exist_ok=True)
    os.makedirs(f"{output_dir}/result", exist_ok=True)

    # 载入内部资源
    ref = get_resource_path('CYP2D6.1.001.fa')
    haplo = get_resource_path('CYP2D6.haplotypes_core.fasta')
    refseq_gene_core = get_resource_path('RefSeqGeneCore')

    # 载入 minimap2, k8-Linux, 和 paftools.js
    minimap2_path = get_resource_path('minimap2/minimap2')
    k8_path = get_resource_path('k8-0.2.4/k8-Linux')
    paftools_path = get_resource_path('minimap2/misc/paftools.js')

    ### Mapping ###
    paf_file = f"{output_dir}/alignment/mapping.paf"
    run_command(f"{minimap2_path} -cx splice:hq -G13k -y --cs -t32 -2 {sample} {ref} > {paf_file}")

    ### Extract Reads ###
    extract_dir = f"{output_dir}/extract"
    extract_loci_from_paf_script(sample, paf_file, extract_dir)
    print("Extract reads: Finished")
    
    ### Sorting Reads ###
    for fasta_file in os.listdir(extract_dir):
        if fasta_file.endswith(".fasta"):
            fasta_path = os.path.join(extract_dir, fasta_file)
            output_paf = os.path.join(extract_dir, fasta_file.replace(".fasta", ".paf"))
            run_command(f"{minimap2_path} -cx splice:hq -G13k -y --cs -t32 -2 {ref} {fasta_path} | sort -k10,10n > {output_paf}")
    print("Sorting Reads: Finished")
    
    ### Variant Calling ###
    for paf_file in os.listdir(extract_dir):
        if paf_file.endswith(".paf"):
            input_paf = os.path.join(extract_dir, paf_file)
            output_vcf = os.path.join(extract_dir, paf_file.replace(".paf", ".vcf"))
            run_command(f"{k8_path} {paftools_path} call -L3 -l3 -f {ref} {input_paf} > {output_vcf}")
    print("Variant Calling: Finished")
    
    ### Annotation ###
    result_dir = f"{output_dir}/result"
    counter = 1
    for fasta_file in os.listdir(extract_dir):
        if fasta_file.endswith(".fasta"):
            fasta_path = os.path.join(extract_dir, fasta_file)
            output_paf = os.path.join(result_dir, f"comparison_{counter}.paf")
            run_command(f"{minimap2_path} -cx splice:hq -G13k -y --cs -t32 -2 {haplo} {fasta_path} > {output_paf}")
            counter += 1
    
    counter = 1
    for vcf_file in os.listdir(extract_dir):
        if vcf_file.endswith(".vcf"):
            vcf_path = os.path.join(extract_dir, vcf_file)
            output_txt = os.path.join(result_dir, f"comparison_{counter}.txt")
            run_anotation_script(vcf_path, refseq_gene_core, output_txt)
            counter += 1
    print("Annotating: Finished")
    
    ### Comparison ###
    counter = 1
    stop_processing = False

    for comparison_file in sorted(os.listdir(result_dir)):
        if not comparison_file.startswith("comparison_") or not comparison_file.endswith(".txt"):
            continue
        
        paf_file = os.path.join(result_dir, f"comparison_{counter}.paf")
        allele_output = os.path.join(result_dir, f"allele_{counter}.txt")
        run_comparison_script(os.path.join(result_dir, comparison_file), paf_file, allele_output)
        
        with open(allele_output, "r") as f:
            if "*5" in f.read():
                print(f"*5 found in {allele_output}. Stopping the process.")
                
                for file in os.listdir(result_dir):
                    if file.startswith("allele_") and file.endswith(".txt"):
                        os.remove(os.path.join(result_dir, file))
                with open(os.path.join(result_dir, "allele_1.txt"), "w") as output_file:
                    output_file.write("*5")
                stop_processing = True
                break
        
        counter += 1
        
        if stop_processing:
            break
    
    print("Job Finished")

if __name__ == "__main__":
    main()


