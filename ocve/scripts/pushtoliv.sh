#!/usr/bin/env bash

dump_dir="/vol/ocve3/dumps/"
log_file="${dump_dir}/pushtoliv.log"
stg_dump="${dump_dir}pg_stg_dump.sql"
live_dump="${dump_dir}pg_liv_dump.sql"

echo "Pushtolive begin $(date +%F_%T) \n" >> ${log_file}
#Backup staging
pg_dump -w -c -O -h db-pg-1.cch.kcl.ac.uk -U app_ocve -t ocve_* app_ocve_merged_stg > ${stg_dump} 2>${log_file}
#Backup Live
pg_dump -w -c -O -h db-pg-1.cch.kcl.ac.uk -U app_ocve app_ocve_merged > ${live_dump} 2>${log_file}
#Upload staging to live if file ok
if [ -fs $stg_dump ]; then

    #Compress backups
    tar -czf ${dump_dir}/stg_dump.tar.gz ${stg_dump}
    tar -czf ${dump_dir}/liv_dump.tar.gz ${live_dump}
    #Add line to log

fi