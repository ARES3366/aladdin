function init_face_database(){
    print("init face_info mongoDB...");
    client = new Mongo();
    db = client.getDB("aladdin_cas");
    res = [
        db.tbl_face_info.drop(),
        db.tbl_face_info.drop(),

        // 单键排序索引
        db.tbl_face_info.createIndex({"face_id" : 1}),

        // 复合排序索引
        db.tbl_face_info.createIndex({"url" : 1, "face_id" : 1}),
    ];
    printjson(res);
    return true;
};

function init_image_search_database(){
    print("init image_meta_data mongoDB...");
    client = new Mongo();
    db = client.getDB("aladdin_cas");
    res = [
        db.object_detection.drop(),
        db.object_detection.drop(),
        db.object_detection.createIndex({"url": 1}),
        db.object_detection.createIndex({"vid": 1})

    ];
    printjson(res);
    return true;
}


try{
    let res = init_face_database();
    let image_search_res = init_image_search_database();
} catch (e){
    print(e);
    quit(1);
};
