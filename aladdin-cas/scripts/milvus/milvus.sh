curl -X DELETE "http://aladdin-cas-milvus:19121/collections/face_recognition" || true
curl -X POST "http://aladdin-cas-milvus:19121/collections" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"collection_name\":\"face_recognition\",\"dimension\":128,\"index_file_size\":1024,\"metric_type\":\"L2\"}" || true
curl -X POST "http://aladdin-cas-milvus:19121/collections/face_recognition/indexes" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"index_type\":\"IVFPQ\",\"params\": {\"m\":64,\"nlist\":1000}}" || true
curl -x DELETE "http://aladdin-cas-milvus:19121/collections/object_detection" || true
curl -X POST "http://aladdin-cas-milvus:19121/collections" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"collection_name\":\"object_detection\",\"dimension\":128,\"index_file_size\":1024,\"metric_type\":\"L2\"}" || true
for tag in {0..999}
do
curl -X POST "http://aladdin-cas-milvus:19121/collections/object_detection/partitions" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"partition_tag\": \"$tag\"}"
done
curl -X POST "http://aladdin-cas-milvus:19121/collections/object_detection/indexes" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"index_type\":\"IVFPQ\",\"params\": {\"m\":16,\"nlist\":1024}}" || true
