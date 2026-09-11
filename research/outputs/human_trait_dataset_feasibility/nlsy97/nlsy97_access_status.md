# NLSY97 public-data access status

**Status: ACCESS OBTAINED.** On 2026-09-11, the official NLS Investigator guest workflow produced a public-use extract with 8,984 rows and 126 columns. No account, CAPTCHA bypass, or access-control circumvention was used. The final selected reference numbers are preserved in `human_trait_dataset_feasibility_final.NLSY97` in the gitignored raw-data directory, and the full committed variable manifest records every selected variable.

The official route is https://www.nlsinfo.org/investigator/pages/search. NLS Investigator documentation states that an account is not needed to browse public data, although an account is needed to save datasets online. The downloaded respondent-level CSV, data file, control files, codebook, and ZIP remain under `data_external/human_validation/nlsy97/public_use_extract/`, which is gitignored.

Restricted geocodes were neither requested nor obtained. Military specialty questions are public questionnaire content, but this extraction retains the public military-employer flags and general 2002 Census occupation codes; known coding caveats for military specialty strings remain relevant. Later work involving fine geography or restricted fields would require a separate BLS restricted-data application.
