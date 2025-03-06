import os
import subprocess
import argparse

# 設定固定參數
REF = "CYP2D6.1.001.fa"
HAPLO = "CYP2D6.haplotypes_core.fasta"
REFSEQ_GENE_CORE = "RefSeqGeneCore"

# 從環境變量獲取 minimap2 和 k8 的路徑
MINIMAP2_PATH = os.getenv("MINIMAP2_PATH", None)
K8_PATH = os.getenv("K8_PATH", None)

# 檢查工具是否存在
if MINIMAP2_PATH is None or K8_PATH is None:
    print("Error: MINIMAP2_PATH or K8_PATH environment variable is not set.")
    print("Please make sure to set the environment variables or run the install_dependencies.sh script.")
    exit(1)

def run_command(command):
    """執行 shell 指令並顯示輸出"""
    print(f"Running: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    parser = argparse.ArgumentParser(description="CYP2D6 Analysis Pipeline")
    parser.add_argument("--sample", required=True, help="Path to the sample FASTA file")
    parser.add_argument("--samplename", required=True, help="Sample name (e.g., HG01258P)")
    parser.add_argument("--output", required=True, help="Output directory")

    args = parser.parse_args()

    sample = args.sample
    samplename = args.samplename
    output_dir = os.path.join(args.output, samplename)

    # 建立輸出資料夾
    os.makedirs(f"{output_dir}/alignment", exist_ok=True)
    os.makedirs(f"{output_dir}/extract", exist_ok=True)
    os.makedirs(f"{output_dir}/result", exist_ok=True)

    # 設定環境變數
    os.environ["PATH"] = f"{MINIMAP2_PATH}:{K8_PATH}:" + os.environ["PATH"]

    ### Mapping ###
    paf_file = f"{output_dir}/alignment/mapping.paf"
    run_command(f"minimap2 -cx splice:hq -G13k -y --cs -t32 -2 {sample} {REF} > {paf_file}")

    ### Extract Reads ###
    extract_dir = f"{output_dir}/extract"
    run_command(f"python3 extract_loci_from_paf.py {sample} {paf_file} {extract_dir}")
    
    print("Extract reads: Finished")

    ### Sorting ###
    for fasta_file in os.listdir(extract_dir):
        if fasta_file.endswith(".fasta"):
            fasta_path = os.path.join(extract_dir, fasta_file)
            output_paf = os.path.join(extract_dir, fasta_file.replace(".fasta", ".paf"))
            run_command(f"minimap2 -cx splice:hq -G13k -y --cs -t32 -2 {REF} {fasta_path} | sort -k10,10n > {output_paf}")

    print("Sorting Reads: Finished")

    ### Variant Calling ###
    for paf_file in os.listdir(extract_dir):
        if paf_file.endswith(".paf"):
            input_paf = os.path.join(extract_dir, paf_file)
            output_vcf = os.path.join(extract_dir, paf_file.replace(".paf", ".vcf"))
            run_command(f"k8-Linux paftools.js call -L3 -l3 -f {REF} {input_paf} > {output_vcf}")

    print("Variant Calling: Finished")

    ### Annotation ###
    result_dir = f"{output_dir}/result"
    counter = 1
    for fasta_file in os.listdir(extract_dir):
        if fasta_file.endswith(".fasta"):
            fasta_path = os.path.join(extract_dir, fasta_file)
            output_paf = os.path.join(result_dir, f"comparison_{counter}.paf")
            run_command(f"minimap2 -cx splice:hq -G13k -y --cs -t32 -2 {HAPLO} {fasta_path} > {output_paf}")
            counter += 1

    counter = 1
    for vcf_file in os.listdir(extract_dir):
        if vcf_file.endswith(".vcf"):
            vcf_path = os.path.join(extract_dir, vcf_file)
            output_txt = os.path.join(result_dir, f"comparison_{counter}.txt")
            run_command(f"python3 anotation.py {vcf_path} {REFSEQ_GENE_CORE} {output_txt}")
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

        run_command(f"python3 comparison.py {os.path.join(result_dir, comparison_file)} {paf_file} {allele_output}")

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


