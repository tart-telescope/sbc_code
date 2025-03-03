rsync --verbose -rv --exclude="config/*.sqlite" --exclude="config/*.key" --exclude="hs_data/*" . tart@cloud.elec.ac.nz:headscale
