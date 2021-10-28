#!/bin/sh
pyinstaller server.py -n aladdin-cas -y --hidden-import="sklearn.neighbors._typedef" \
    --hidden-import="sklearn.utils._cython_blas" \
	--hidden-import="sklearn.tree._utils" \
	--hidden-import="sklearn.neighbors._quad_tree" \
	--hidden-import="csr_matmat_pass1" \
	--hidden-import="scipy.special.cython_special" \
    --hidden-import="sklearn.neighbors._typedefs" \

# pyinstaller -F  aladdin-cas.spec -y 
cd dist/aladdin-cas

python_lib_dir=/usr/local/lib/python3.6/site-packages

subdir=jieba/analyse
mkdir -p $subdir
\cp -f ${python_lib_dir}/jieba/dict.txt jieba/dict.txt
\cp -f ${python_lib_dir}/${subdir}/idf.txt ${subdir}/idf.txt


#for fn in `find /usr/local/lib/python3.6/site-packages/tensorflow/contrib -name "*.so"`
#do
#	dir=`dirname $fn`
#	mkdir -p $dir
#	echo "mkdir -p $dir"
#	subdir=${dir##*site-packages/}
#	mkdir -p $subdir
#	cp $fn $subdir
#done

mkdir -p xpinyin
cp /usr/local/lib/python3.6/site-packages/xpinyin/Mandarin.dat xpinyin

cp -rfp ../../model ./
cp -rfp ../../predata ./
cp -rfp ../../conf ./
mkdir -p protos
echo $pwd
cp -rfp ../../protos/* protos/ 
cp -rfp ../../dic dic

mkdir -p codebook
cp -rfp ../../match_image/delg_codebook codebook

mkdir -p privacy_information_identity/property && cp -rfp ../../privacy_information_identity/property/default.json privacy_information_identity/property/default.json
mkdir -p privacy_information_identity/property && cp -rfp ../../privacy_information_identity/property/defined.json privacy_information_identity/property/defined.json
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/bank.txt privacy_information_identity/dic/bank.txt
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/date.txt privacy_information_identity/dic/date.txt
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/email.txt privacy_information_identity/dic/email.txt
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/id.txt privacy_information_identity/dic/id.txt
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/passport.txt privacy_information_identity/dic/passport.txt
mkdir -p privacy_information_identity/dic && cp -rfp ../../privacy_information_identity/dic/telephone.txt privacy_information_identity/dic/telephone.txt
mkdir -p object_detection && cp -rfp ../../object_detection/support_collection.npy object_detection/
mkdir -p mkdir face_recognition_models && cp -rp /usr/local/lib/python3.6/site-packages/face_recognition_models/models/ face_recognition_models/models
mkdir -p astor && cp /usr/local/lib/python3.6/site-packages/astor/VERSION astor/VERSION

pip3 freeze > requirements.txt

cd ../../
