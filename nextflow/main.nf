

params.input_file = "input.mzML"
params.mini = 500

Channel
    .fromPath( params.input_file )
    .set { input_file }
 

process biosaur {
    container '116457570579.dkr.ecr.us-east-2.amazonaws.com/biosaur'

    publishDir "features/", mode: 'copy'
   
    cpus 2
    memory '12 GB'
    
    input:
    path mzml from input_file

    output:
    path  "${mzml}.tsv" into feature_out

    script:
    """
    biosaur \
        -mini ${params.mini} \
        -np $task.cpus \
        -out ${mzml}.tsv \
        ${mzml} 
    """
}

