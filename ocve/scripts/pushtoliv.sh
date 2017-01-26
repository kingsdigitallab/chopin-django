#!/bin/bash
#A simple shell script to push OCVE/CFEO data from stg to liv
#DOES NOT push wagatil data
#EH 31/10/2016

dump_dir="/vol/ocve3/dumps/"
log_file="${dump_dir}/pushtoliv.log"
stg_dump="${dump_dir}pg_stg_dump.sql"
live_dump="${dump_dir}pg_liv_dump.sql"
notes_dump="${dump_dir}notes_liv_dump.sql"

printf "Pushtolive begin $(date +%F_%T) \n" >> ${log_file}

#Backup Live
pg_dump -w -c -O -h db-pg-1.cch.kcl.ac.uk -U app_ocve app_ocve_merged > ${live_dump} 2>>${log_file}

#Backup staging
pg_dump -w -c -O -h db-pg-1.cch.kcl.ac.uk -U app_ocve -t ocve_*  app_ocve_merged_stg > ${stg_dump} 2>>${log_file}

#Upload staging to live if file ok
if [ -s $stg_dump ]; then
    #Add line to log
    printf "$(date +%F_%T): Uploading to live \n" >> ${log_file}
    #Backup notes from live
    pg_dump -w -a -h db-pg-1.cch.kcl.ac.uk --table=ocve_annotation_barregion --table=ocve_annotation -U app_ocve app_ocve_merged > ${notes_dump} 2>>${log_file}

    #delete notes set on live
    psql app_ocve_merged -c "delete from ocve_annotation_barregion;"
    psql app_ocve_merged -c "delete from ocve_annotation;"

    #upload to live
    psql -w -h db-pg-1.cch.kcl.ac.uk -U app_ocve app_ocve_merged < ${stg_dump} 2>>${log_file}

    #restore notes to live
    psql -w -h db-pg-1.cch.kcl.ac.uk -U app_ocve app_ocve_merged < ${notes_dump} 2>>${log_file}

    #Rebuild website data on liv

    #Create missing thumbnails
    
else
    printf "ERROR: staging dump not generated.  Upload aborted \n"
fi
printf "$(date +%F_%T): pushtolive complete \n" >> ${log_file}




























