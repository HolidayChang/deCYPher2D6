from setuptools import setup, find_packages

setup(
    name="deCYP2D6",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "deCYP2D6": [
            "CYP2D6.1.001.fa",
            "CYP2D6.haplotypes_core.fasta",
            "CYP2D6.1.001.fa.fai",
            "RefSeqGeneCore/*.vcf",  # 確保打包所有 VCF 檔案
            "minimap2/minimap2",  # 內建 minimap2
            "k8-0.2.4/k8-Linux",  # 內建 k8
            "minimap2/misc/paftools.js"  # 內建 paftools.js
        ]
    },
    entry_points={
        'console_scripts': [
            'decyp2d6=deCYP2D6.decyp2d6:main',
        ],
    },
)




