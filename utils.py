import numpy as np
from tqdm import tqdm
import pandas as pd
import json
import gzip
import time
import re
import requests
from functools import wraps

def generate_config_xml(model_name, params, output_dir='./tmp_config'):
    """
    Dynamically generate schema.xml and solrconfig.xml for various indexing algorithms.

    model_name: str
      Select model_name of 'hnsw' or 'cuvs'.

    params: dict(str)
      Specify relevant set of parameters for the model_name selected.
    """
    print(f'Generating {model_name} schema.xml and solrconfig.xml files.')
    
    if model_name == 'hnsw':
        dim = params['dim']
        hnswMaxConnections = params['hnswMaxConnections']
        hnswBeamWidth = params['hnswBeamWidth']
        
        # Build params: hnswBeamWidth=efConstruction, hnswMaxConnections=M.
        # No efSearch parameter available.
        
        schema_xml = f'''<?xml version="1.0" ?>
        <!--
         Licensed to the Apache Software Foundation (ASF) under one or more
         contributor license agreements.  See the NOTICE file distributed with
         this work for additional information regarding copyright ownership.
         The ASF licenses this file to You under the Apache License, Version 2.0
         (the "License"); you may not use this file except in compliance with
         the License.  You may obtain a copy of the License at
        
             http://www.apache.org/licenses/LICENSE-2.0
        
         Unless required by applicable law or agreed to in writing, software
         distributed under the License is distributed on an "AS IS" BASIS,
         WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
         See the License for the specific language governing permissions and
         limitations under the License.
        -->
        
        <!-- Test schema file for DenseVectorField -->
        
        <schema name="schema-densevector" version="1.7">
        
            <fieldType name="string" class="solr.StrField" multiValued="true"/>
            <fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="{dim}" knnAlgorithm="hnsw" hnswMaxConnections="{hnswMaxConnections}" hnswBeamWidth="{hnswBeamWidth}" similarityFunction="cosine" />
            <fieldType name="plong" class="solr.LongPointField" useDocValuesAsStored="false"/>
        
            <field name="id" type="string" indexed="true" stored="true" multiValued="false" required="false"/>
            <field name="title" type="string" indexed="true" stored="true" multiValued="false" required="false"/>
            <field name="article_vector" type="knn_vector" indexed="true" stored="true"/>
            <field name="article" type="string" indexed="true" stored="true"/>
        
            <field name="_version_" type="plong" indexed="true" stored="true" multiValued="false" />
            <uniqueKey>id</uniqueKey>
        </schema>
        '''

        # No params modified in solrconfig.xml for hnsw.
        solrconfig_xml = '''<?xml version="1.0" ?>
        <!--
          This software was produced for the U. S. Government
          under Contract No. W15P7T-11-C-F600, and is
          subject to the Rights in Noncommercial Computer Software
          and Noncommercial Computer Software Documentation
          Clause 252.227-7014 (JUN 1995)
        
          Copyright 2013 The MITRE Corporation. All Rights Reserved.
        
          Licensed under the Apache License, Version 2.0 (the "License");
          you may not use this file except in compliance with the License.
          You may obtain a copy of the License at
        
              http://www.apache.org/licenses/LICENSE-2.0
        
          Unless required by applicable law or agreed to in writing, software
          distributed under the License is distributed on an "AS IS" BASIS,
          WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
          See the License for the specific language governing permissions and
          limitations under the License.
          -->
        
        <!-- a basic solrconfig that tests can use when they want simple minimal solrconfig/schema
             DO NOT ADD THINGS TO THIS CONFIG! -->
        <config>
            <luceneMatchVersion>${tests.luceneMatchVersion:LATEST}</luceneMatchVersion>
            <dataDir>${solr.data.dir:}</dataDir>
            <directoryFactory name="DirectoryFactory" class="${solr.directoryFactory:solr.NRTCachingDirectoryFactory}"/>
        
            <!-- for postingsFormat="..." -->
        
            <!-- since Solr 4.8: -->
            <requestHandler name="/select" class="solr.SearchHandler"></requestHandler>
        
        </config>
        '''
        
    elif model_name == 'cuvs':
        dim = params['dim']
        cuvsWriterThreads = params['cuvsWriterThreads']
        graphDegree = params['graphDegree']
        intGraphDegree = params['intGraphDegree']

        schema_xml = f'''<?xml version="1.0" ?>
        <!--
         Licensed to the Apache Software Foundation (ASF) under one or more
         contributor license agreements.  See the NOTICE file distributed with
         this work for additional information regarding copyright ownership.
         The ASF licenses this file to You under the Apache License, Version 2.0
         (the "License"); you may not use this file except in compliance with
         the License.  You may obtain a copy of the License at
        
             http://www.apache.org/licenses/LICENSE-2.0
        
         Unless required by applicable law or agreed to in writing, software
         distributed under the License is distributed on an "AS IS" BASIS,
         WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
         See the License for the specific language governing permissions and
         limitations under the License.
        -->
        
        <!-- Test schema file for DenseVectorField -->
        
        <schema name="schema-densevector" version="1.7">
        
            <fieldType name="string" class="solr.StrField" multiValued="true"/>
            <fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="{dim}" knnAlgorithm="cuvs" similarityFunction="cosine" />
            <fieldType name="plong" class="solr.LongPointField" useDocValuesAsStored="false"/>
        
            <field name="id" type="string" indexed="true" stored="true" multiValued="false" required="false"/>
            <field name="title" type="string" indexed="true" stored="true" multiValued="false" required="false"/>
            <field name="article_vector" type="knn_vector" indexed="true" stored="true"/>
            <field name="article" type="string" indexed="true" stored="true"/>
        
            <field name="_version_" type="plong" indexed="true" stored="true" multiValued="false" />
            <uniqueKey>id</uniqueKey>
        </schema>
        '''

        solrconfig_xml = f'''<?xml version="1.0" ?>
        <!--
          This software was produced for the U. S. Government
          under Contract No. W15P7T-11-C-F600, and is
          subject to the Rights in Noncommercial Computer Software
          and Noncommercial Computer Software Documentation
          Clause 252.227-7014 (JUN 1995)
        
          Copyright 2013 The MITRE Corporation. All Rights Reserved.
        
          Licensed under the Apache License, Version 2.0 (the "License");
          you may not use this file except in compliance with the License.
          You may obtain a copy of the License at
        
              http://www.apache.org/licenses/LICENSE-2.0
        
          Unless required by applicable law or agreed to in writing, software
          distributed under the License is distributed on an "AS IS" BASIS,
          WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
          See the License for the specific language governing permissions and
          limitations under the License.
          -->
        
        <!-- a basic solrconfig that tests can use when they want simple minimal solrconfig/schema
             DO NOT ADD THINGS TO THIS CONFIG! -->
        <config>
            <luceneMatchVersion>${{tests.luceneMatchVersion:LATEST}}</luceneMatchVersion>
            <dataDir>${{solr.data.dir:}}</dataDir>
            <directoryFactory name="DirectoryFactory" class="${{solr.directoryFactory:solr.NRTCachingDirectoryFactory}}"/>
        
            <!-- for postingsFormat="..." -->
            <codecFactory name="CodecFactory" class="org.apache.solr.core.CuvsCodecFactory">
                <int name="cuvsWriterThreads">{cuvsWriterThreads}</int> 
                <int name="graphDegree">{graphDegree}</int> 
                <int name="intGraphDegree">{intGraphDegree}</int> 
            </codecFactory>
        
            <!-- since Solr 4.8: -->
            <queryParser name="cuvs" class="org.apache.solr.search.neural.CuvsQParserPlugin"/>
            <requestHandler name="/select" class="solr.SearchHandler"></requestHandler>
        
        </config>
        '''
        
    else:
        raise ValueError('Unknown model value. Choose "hnsw" or "cuvs".')
        
    # Write files to disk
    with open(output_dir + '/schema.xml', 'w') as file:
        file.write(schema_xml)

    with open(output_dir + '/solrconfig.xml', 'w') as file:
        file.write(solrconfig_xml)

    print('Completed writing all XML files.')
    return()

def generate_solr_bash_scripts(data_dir, use_hw='cpu', jvm_mem='4G'):
    """
    Function for generating bash scritps to launch Solr, upload data, and start indexing.

    data_dir: str
      Directory with javabin formated vector data.

    use_hw: str
      Select hardware to use. Choose from 'cpu' or 'gpu'.

    jvm_mem: str
      Heap memory allocation for Java. Default is '4G' for 4GB.
    """
    
    start_solr_mod_sh = f'''#!/bin/bash
    # Select hardware accelerator (cpu or gpu)
    export use_hw={use_hw}
    export jvm_mem={jvm_mem}
    
    # Stop Solr if running
    pkill -9 java # kill all java processes
    rm -rf solr-10.0.0-SNAPSHOT
    wait 30
    
    # Start a Solr instance
    tar -xf solr-10.0.0-SNAPSHOT.tgz
    cd solr-10.0.0-SNAPSHOT
    bin/solr start -m $jvm_mem --force
    
    # ./tmp_config dir contains dynamically generated Solr config xml files
    (cd ../tmp_config && zip -r - *) | curl -X POST --header "Content-Type:application/octet-stream" --data-binary @- "http://localhost:8983/solr/admin/configs?action=UPLOAD&name=$use_hw"
    curl "http://localhost:8983/solr/admin/collections?action=CREATE&name=test&numShards=1&collection.configName=$use_hw"
    '''
    
    # Removed internal timing function from upload_all_files_mod.sh script
    upload_files_mod_sh = f'''#!/bin/bash
    
    # Define the URL endpoint
    URL="http://localhost:8983/solr/test/update?commit=true&overwrite=false"
    
    # Define the directory containing files to upload
    
    DIRECTORY="{data_dir}"
    # install httpie
    # Loop through each file in the directory and post it in the background
    for FILE in "$DIRECTORY"/*; do
        if [ -f "$FILE" ]; then  # Check if it's a file
            echo "Uploading $FILE..."
            http --ignore-stdin POST "$URL" Content-Type:application/javabin @"$FILE" &
        fi
    done
    
    wait
    
    # Wait for all background processes to finish
    echo "All files in the directory uploaded."
    '''
    
    # Write files to disk
    with open('./start_solr_mod.sh', 'w') as file:
        file.write(start_solr_mod_sh)
    
    with open('./upload_all_files_mod.sh', 'w') as file:
        file.write(upload_files_mod_sh)

    print('Sucessfully written ./start_solr_mod.sh and ./upload_all_files_mod.sh.')
    return()

def load_query_vectors(data_file, num_queries=8192, jar_classpath='./solr-cuvs-benchmarks-1.0-SNAPSHOT-jar-with-dependencies.jar'):
    """
    Load vectors from data_file (javabin). Take the first num_queries vectors to use as query vectors.
    """
    # Read vectors from javabin file
    import jpype
    import jpype.imports
    
    # Start the JVM, adjust classpath to include the relevant Java libraries
    try:
        jpype.startJVM(classpath=[jar_classpath])
    except:
        print('Skiping startJVM. JVM already running.')
    
    # Load JavaBinCodec from jar
    from org.apache.solr.common.util import JavaBinCodec
        
    # Use JavaBinCodec to read the file.
    codec = JavaBinCodec()
    with open(data_file, 'rb') as f:
        java_input_stream = jpype.JClass('java.io.ByteArrayInputStream')(f.read())
        obj = codec.unmarshal(java_input_stream)
    
    # First column is 'id'. Second column is 'article_vector'.
    # data0 = [(obj[ii]['id'], obj[ii]['article_vector']) for ii in range(num_queries)]
    
    # Separate ids and article vectors:
    ids = [int(str(obj[ii]['id'])) for ii in range(num_queries)]
    
    # Convert to vector array into str and remove white spaces
    query_vectors = [re.sub(r'[ \n]+', '', str(obj[ii]['article_vector'].toArray())) for ii in range(num_queries)]
    print('Successfully loaded query vectors.')
    return(ids, query_vectors)