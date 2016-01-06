import os
import re
import pandas as pd

newdir = "C:\Users\Owner\Box Sync\mutsig\\"
snpdir = "C:\Users\Owner\Box Sync\oncotator\oncotator_snps\\"
indeldir = "C:\Users\Owner\Box Sync\oncotator\oncotator_indel\\"

for subdir, dirs, files in os.walk(snpdir):
    #input the directory you want to walk through full of the oncotate files
    fw = open(newdir + "gistsnp_somatic_oncotate.txt", 'w')
    #fw = open(newdir + file.replace("_merged_sort_mutect_filt_annotated", "_somatic_oncotate"), 'w')
    fh = open(snpdir + files[1], 'r')
    lines = fh.readlines()
    fw.write(str(lines[100]))#write column names/header into the master file
    fh.close()
    norm_match=[]
    tumor_samp=[]
    for file in files:
        fh = open(snpdir + file, 'r')  # use the absolute URL of the file
        lines = fh.readlines()
        for line in lines[101:]:
            field = re.split(r'\t', line)
            if int(field[302]) == 2:
                tumor_samp.append(field[16])
                fw.write(str(line))
            elif int(field[302]) == 0:
                norm_match.append(field[16])
        fh.close()
    fw.close()

#Change the sample barcode names for the final maf file
#Replace UNKNOWN barcode columns with list of column names made above
#dat = pd.read_table(newdir + "gists_somatic_oncotate.txt")
#replace the tumor and normal barcodes
snpdat=  pd.DataFrame.from_csv(newdir + "gistsnp_somatic_oncotate.txt", header=0, sep="\t")
snpdat.Tumor_Sample_Barcode=tumor_samp
snpdat.Matched_Norm_Sample_Barcode=norm_match
#cols = snpdat.columns.tolist()
snpdat.to_csv(newdir + "gistsnp_somatic_oncotate.maf.txt", sep="\t")
#only use snps where read depth was equal or above 20
snpdat=snpdat[snpdat['read_depth'] > 19]

snpdat.to_csv(newdir + "gistsnp_somatic_oncotate_q20.maf.txt", sep="\t")

for subdir, dirs, files in os.walk(indeldir):
#for files in os.listdir(indeldir):
    fw = open(newdir + "gistsindel_somatic_oncotate.txt", 'w')
    fh = open(indeldir + files[1], 'r')
    lines = fh.readlines()
    fw.write(str(lines[8]))#write column names/header into the master file
    fh.close()
    tumor_samp=[]
    norm_samp=[]
    nlstr = re.compile('.*Normal.*|.*normal.*|.*NL.*|.*Norm.*')
    for file in files:
        fh = open(indeldir + file, 'r')  # use the absolute URL of the file
        lines = fh.readlines()
        for line in lines[9:]:
            field = re.split(r'\t', line)
            if field[303]=="True\n":
                if nlstr.match(field[16]):
                    norm_samp.append(field[16])
                else:
                    tumor_samp.append(field[16])
                    fw.write(str(line))
        print file
        fh.close()
    fw.close()

#Change the sample barcode names for the final maf file
#Replace UNKNOWN barcode columns with list of column names made above
#dat = pd.read_table(newdir + "gists_somatic_oncotate.txt")
#replace the tumor and normal barcodes
indeldat=  pd.DataFrame.from_csv(newdir + "gistsindel_somatic_oncotate.txt", header=0, sep="\t")
indeldat.Tumor_Sample_Barcode=tumor_samp
indeldat.Matched_Norm_Sample_Barcode=norm_samp
indeldat.to_csv(newdir + "gistsindel_somatic_oncotate.maf.txt", sep="\t")

#only use snps where read depth was equal or above 20
indeldat=indeldat[indeldat['T_DP'] > 19]
indeldat.to_csv(newdir + "gistsindel_somatic_oncotate_q20.maf.txt", sep="\t")



#Combining the snps and indels into a single mafs
snpdat_trunc=snpdat.ix[:,0:41]
indel_trunc=indeldat.ix[:,0:41]

mut_dat = pd.concat([snpdat_trunc, indel_trunc])
mut_dat.to_csv(newdir + "combo_muts.maf.txt", sep="\t")

