/*
# Author: Ivar Vargas Belizario
# Copyright (c) 2021
# E-mail: ivar@usp.br
*/


function showloading() {
    gelem("idloading").style.display = "block";
}
function hideloading() {
    gelem('idloading').style.display = "none";
}



function ServiceData(pname) {
    var self = this;
    this.in = {"argms": {"type": 0}};
    this.ou = '';
    this.event = function () { };
    this.start = function () {
        var ps = MOPRO.pushprocess(pname);
        try {
            var url = "./query?data=" + JSON.stringify(self.in);
            d3.json(url).then(function(data){
                self.ou = data;
                self.event();
                MOPRO.popprocess(ps);
            });
        }
        catch (err) {
            MOPRO.popprocess(ps);
            console.log(err);
        }
    };
}









function framework() {
    var self = this;

    this.mw = new ModalWindow();
    //console.log("this.mw", self.mw);
    this.VertexColorF = null;
    this.layoutprojection = null;   
    this.isnamedbedited = true;
    this.homepath = "/";
    this.path = "";
    this.file = "";
    this.stack = Array(100).fill("");
    this.stacki = 0;
    this.width = 100;
    this.height = 100;
    this.data = [];
    this.contours = [];
    this.targets = [];
    this.selectroids = [];
    this.pjpath = null;
    this.idpj = null;
    this.labels = null;
    this.ypredicted = null;
    //this.ypredicted = null;
    this.setToolpiltex = function (ex, ey, txt) {
        gelem("toolpiltex").innerHTML = "";
        gelem('toolpiltex').style.left = (ex + 2) + "px";
        gelem('toolpiltex').style.top = (ey - 23) + "px";
        gelem('toolpiltex').style.display = "block";
        gelem("toolpiltex").innerHTML = txt;
    };

    this.hideToolpiltex = function () {
        gelem("toolpiltex").style.display = "none";
        gelem("toolpiltex").innerHTML = "";
    };

    this.setToolpiltexParc = function (ex, ey, i) {
        txt = self.data.points[i]["u"]+" : "+self.data.idinstancelabel[i];
        txt += `<br><img src="https://docs.microsoft.com/pt-br/windows/apps/design/style/images/header-sound.svg" width="100">`;
        
        self.setToolpiltex(ex, ey, txt);
    };
    
    this.opengallery = function(){
        gelem("lyimgpanel").style.display = "none";
        gelem("lylistpanel").style.display = "block";

        gelem("lylistview").innerHTML = "";
        var ob = new ServiceData("load gallery");
        ob.in.argms["type"] = 8;
        ob.event = function () {
            self.data = this.ou["response"];
            console.log("rexxxxr", self.data);
            self.listimagestable();
            //self.statusthread();
        };
        ob.start();
    };
    
    this.listimagestable = function(){
        var txtx = "";
        txtx = `
        <div class="tableFixHead">
        <table class="tablex2 table-striped table-sm btn-table" style="background-color: #fff; width: 100%;">
            <thead>
            <tr>
                <th style="text-align:left">Name</th>
                <th style="width: 70px;">Status</th>
                <th style="width: 120px;">Update</th>
                <th style="width: 120px;">Actions</th>
            <tr>
            </thead>
            <tbody>
        `;
        for(var i in self.data){
            re = self.data[i];
            console.log("rex3r", re);
            projectid = re["y"]+"/"+re["m"]+"/"+re["_id"];
            //txtx += `<img src="data/`+re[i]["name"]+`" style="height: 80px; margin: 5px;"
            //            onclick="SCB.chosseimage('data/`+re[i]["name"]+`')";
            //        >`;
            txtx += `
            <tr onclick="
                SCB.openproject('`+projectid+`','`+re["_id"]+`');
                "

                title = "`+projectid+`"
            >
                <td class="align-middle"  style="text-align:left">
                    `+re["name"]+`
                </td>
                <td class="align-middle">`;

            if (re["status"]==1){
                txtx += `<div>
                <i class="fa fa-check-circle" style="color: #0059b3"></i>
                </div>`;
            }
            else{
                txtx += `<div>
                <i class="fas fa-cog fa-spin" style="color: #ff0000"></i>
                </div>`;
            }   
            txtx += `
                </td>
                <td class="align-middle">
                    `+re["date_update"]+`
                </td>
                <td class="align-middle">
                    <a href="#" class="btn btn-light" style="padding: 2px;" title="Downlod dataset" 
                        onclick="
                            //xxx.downloaddataset('5f52b46265aed74204758191');
                        "
                    >
                        <i class="fa fa-download fa-lg" style="color: #f5a742;"></i>
                    </a>
                    <a href="#" class="btn btn-light" style="padding: 2px;" title="Drop dataset"
                        onclick="
                            //xxx.dropdataset('5f52b46265aed74204758191');
                        "
                    >
                        <i class="fa fa-trash fa-lg" style="color: #ff0000;"></i>
                    </a>
                </td>
            </tr>
            `;
        }
        txtx += `
        </tbody>
        </table>
        </div>
        <div style="height: 65px;"></div>
        `;
        gelem("lylistview").innerHTML = txtx;            
        gelem("idimginfo").innerHTML = "";
    };

    this.opendirectory = function(pathin, direcin){
/*         gelem("lyimgpanel").style.display = "none";
        gelem("lylistpanel").style.display = "block"; */

        gelem("lypaneldirsfiles").innerHTML = "";
        
        var ob = new ServiceData("load gallery");
        ob.in.argms["type"] = 2;
        ob.in.argms["path"] = pathin;
        ob.in.argms["directory"] = direcin;

        ob.event = function () {
            var re = this.ou["response"];
            var err = this.ou["error"];
            //console.log("ss",err);
            if (err==1){
                alert(re);
                return 0;
            }
            path = re["path"];
            files = re["files"];

            self.stack[self.stacki] = path;
            self.stacki++;
    
            gelem("inputpathdir").value = path;

            txtx = `
            <div class="tableFixHead">
            <table class="table table-striped table-sm btn-table" style="background-color: #fff; width: 100%;">
                <thead>
                <tr>
                    <th style="text-align:left">Name</th>
                    <th style="width: 120px;">Modified</th>
                <tr>
                </thead>
                <tbody>
            `;
            for (i in files){
                fi = files[i]
                if(fi["type"]==1){
                    txtx += `
                    <tr 
                        ondblclick="
                            gelem('inputFilevsival').value = '`+fi["name"]+`';
                            SCB.showlayout('frmvsi');
                        "
                    >
                    <td class="align-middle"  style="text-align:left">
                        <i class="fas fa-file-alt" style="color: #333;"></i>
                        &nbsp;`+fi["name"]+`</div>
                    </td>
                    <td class="align-middle"  style="text-align:right">
                        `+fi["date"]+`
                    </td>
                    </tr>`;
                }
                else{
                    txtx += `
                    <tr 
                        ondblclick="
                            SCB.opendirectory('`+path+`','`+fi["name"]+`');
                        "
                        title="`+path+`"
                    >
                    <td class="align-middle"  style="text-align:left">
                        <i class="fa fa-folder" style="color: #256cb8;"></i>
                        &nbsp;`+fi["name"]+`
                    </td>
                    <td class="align-middle"  style="text-align:right">
                        `+fi["date"]+`
                    </td>
                    </tr>`;
                }                
            }
            txtx += "</tbody></table></div>"
            gelem("lypaneldirsfiles").innerHTML = txtx;
        };
        ob.start();
    };

    this.goBack = function(){
        self.stacki = self.stacki-2;
        if (self.stacki< 0){
            self.stacki = 0;
            self.stack[self.stacki] = self.homepath;
        }
        //console.log("EEE",self.stack[self.stacki], self.stacki, self.stack);
        //self.opendirectory(self.stack[self.stacki],'');
    };

    this.showlayout = function(op){
        gelem("lyimgpanel").style.display = "none";
        gelem("lylistpanel").style.display = "none";
        gelem("lyhelppanel").style.display = "none";

        if (op=="gallerylist"){
            gelem("lylistpanel").style.display = "block";
        }
        else if (op=="openproject"){
            gelem("lyimgpanel").style.display = "block";
        }
        else if (op=="help"){
            gelem("lyhelppanel").style.display = "block";
        }
        

    };

    /*  
    this.opendirectory = function(pathin, direcin){

        gelem("lypaneldirsfiles").innerHTML = "";
        
        var ob = new ServiceData("load gallery");
        ob.in.argms["type"] = 2;
        ob.in.argms["path"] = pathin;
        ob.in.argms["directory"] = direcin;

        ob.event = function () {
            var re = this.ou["response"];
            var err = this.ou["error"];


            console.log("ss xxx ",re);
            if (err==1){
                alert(re);
                return 0;
            }
            path = re["path"];
            files = re["files"];

            self.stack[self.stacki] = path;
            self.stacki++;
    
            gelem("inputpathdir").value = path;

            txtx = `
            <div class="tableFixHead">
            <table class="table table-striped table-sm btn-table" style="background-color: #fff; width: 100%;">
                <thead>
                <tr>
                    <th style="text-align:left">Name</th>
                    <th style="width: 120px;">Modified</th>
                <tr>
                </thead>
                <tbody>
            `;
            for (i in files){
                fi = files[i]
                if(fi["type"]==1){
                    txtx += `
                    <tr 
                        ondblclick="
                            SCB.setChooseFile(\``+path+`\`,\``+fi["name"]+`\`);
                        "
                    >
                    <td class="align-middle"  style="text-align:left">
                        <i class="fas fa-file-alt" style="color: #333;"></i>
                        &nbsp;`+fi["name"]+`</div>
                    </td>
                    <td class="align-middle"  style="text-align:right">
                        `+fi["date"]+`
                    </td>
                    </tr>`;
                }
                else{
                    txtx += `
                    <tr 
                        ondblclick="
                            SCB.opendirectory(\``+path+`\`,\``+fi["name"]+`\`);
                        "
                    >
                    <td class="align-middle"  style="text-align:left">
                        <i class="fa fa-folder" style="color: #256cb8;"></i>
                        &nbsp;`+fi["name"]+`
                    </td>
                    <td class="align-middle"  style="text-align:right">
                        `+fi["date"]+`
                    </td>
                    </tr>`;
                }                
            }

            txtx += "</tbody></table></div>"
            gelem("lypaneldirsfiles").innerHTML = txtx;
        };
        ob.start();
    };
     */

    this.setChooseFile = function(path,file){
        self.path = path;
        self.file = file;
        gelem('idinputFilevsival').value = file;
        //console.log(self.path, self.file);
        self.showlayout('frmvsi');
    };
    this.createimgpfromvsi = function(){
        var name = trim(gelem('idFileName').value);
        var factor = (gelem('idnumberfactor').value);

        if (name==""){
            ffocus('idFileName');
            return;
        }
        if (self.path=="" || self.file==""){
            ffocus('idinputFilevsival');
            return;
        }
/*         if (factor>0){
            ffocus('idnumberfactor');
            return;
        } */
            
        var ob = new ServiceData("load gallery");
        ob.in.argms["type"] = 3;
        ob.in.argms["name"] = name;
        ob.in.argms["path"] = self.path;
        ob.in.argms["file"] = self.file;
        ob.in.argms["factor"] = factor;

        ob.event = function () {
            var re = this.ou["response"];
            //console.log("re",re);
            self.opengallery();
            self.showlayout('gallerylist');
        };
        ob.start();
    };

    this.createimgpfromupload = function(){
        gelem("lypaneldirsfiles").innerHTML = "";
                
        var ob = new ServiceData("load gallery");
        ob.in.argms["type"] = 4;
        ob.in.argms["name"] = pathin;
        ob.in.argms["vsifile"] = pathin;
        ob.in.argms["factor"] = direcin;

        ob.event = function () {
            var re = this.ou["response"];

            gelem("lypaneldirsfiles").innerHTML = txtx;
        };
        ob.start();
    };

    // xxxxxxxxxxxx xxxxxxxxxxxxxx
    this.load_roids_as_polygons = function(path){
        var ob = new ServiceData("load roids");
        ob.in.argms["type"] = 5;
        ob.in.argms["path"] = path;

        ob.event = function () {
            //var re = this.ou["response"];
            if (this.ou["error"]==0){
                console.log("poligon....",this.ou["response"]);
                self.selectroids = {};
                self.contours = this.ou["response"];
                //DRW.setContours(this.ou["response"]);
                DRW.drawsegmentation();
            }
        };
        ob.start();
    };

    /* 
    this.statusthread = function(){
        let ob = new ServiceData("load gallery validation");
        ob.in.argms["type"] = 1;
        ob.in["lo"] = false;
        ob.event = function () {
            datax = this.ou["response"];
            console.log("hoxxlax", this.in["lo"]);
            out = false;
            for(i in datax){
                self.data[i] = datax[i];
                if (self.data[i]["atributes"]["status"]==0){
                    out = true;
                }
            }
            if(out){
                setTimeout(function () { self.statusthread(); }, 4000);
            }
            else{
                //self.data = datax;
                self.listimagestable();
            }
        };
        ob.start();        
    };
    */

    this.fullScreen = function () {
        var element = document.documentElement;

        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    };

    this.uploadfiledata = function () {
        var fi = document.getElementById('fileu');
        var file = fi.value;
        var reg = /(.*?)\.(TIFF|tiff)$/;

        //console.log("self.mv", self.mw);
        if (file.match(reg)) {
            var fsize = fi.files.item(0).size;
            var z = Math.round((fsize / 1024));
            if (z <= 71680) {
                let ob = new ServiceData("Upload image");
                ob.in.argms["type"] = 6;
        
                gelem('datafromupload').value = JSON.stringify(ob.in);

                //showloading
                MOPRO.show("Uploading file");
                
                gelem('formupload').submit();        
                gelem('fileu').value = "";        
            }
            else{
                self.mw.alert("","please use files up to 70MB");
            }
        }
        else{
            self.mw.alert("","Please use only .tiff files");
        }
        fi.value = "";
    };

    this.fullScreen = function () {
        var isInFullScreen = (document.fullscreenElement && document.fullscreenElement !== null) ||
        (document.webkitFullscreenElement && document.webkitFullscreenElement !== null) ||
        (document.mozFullScreenElement && document.mozFullScreenElement !== null) ||
        (document.msFullscreenElement && document.msFullscreenElement !== null);

        if (!isInFullScreen) {
            self.setfullScreen();
        } else {
            self.exitfullScreen();
        }
    };

    this.setfullScreen = function () {
        var docElm = document.documentElement;
        if (docElm.requestFullscreen) {
            docElm.requestFullscreen();
        } else if (docElm.mozRequestFullScreen) {
            docElm.mozRequestFullScreen();
        } else if (docElm.webkitRequestFullScreen) {
            docElm.webkitRequestFullScreen();
        } else if (docElm.msRequestFullscreen) {
            docElm.msRequestFullscreen();
        }
    };
    this.exitfullScreen = function () {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    };

    this.updatedatasetname = function (e, newname) {
        newname = trim(newname);
        if (e.keyCode === 13) {

            if (self.isnamedbedited){
                var txtnamedb = newname;
                txtnamedb += `&nbsp;<i class="fas fa-edit fa-sm"></i>`;
                gelem('iddatasettitle').innerHTML = txtnamedb;
                gelem('layoutchangenametxtdb').style.display = 'none';
                gelem('iddatasettitle').style.display = 'block';
    
            }

/*             if (self.datafileselected != "" && newname != "") {
                var ob = new ServiceData("update dataset name");
                ob.in.argms["type"] = 6;
                ob.in.argms["file"] = self.datafileselected;
                ob.in.argms["newname"] = newname;
                ob.event = function () {
                    response = this.ou;
                    self.getdatasetname();
                };
                ob.start();
            } */
        }
    };

    this.makeclassification = function () {
        console.log("self.selectroids.length d", self.selectroids);
        if(Object.keys(self.selectroids).length>0){
            var ob = new ServiceData("make classification");
            ob.in.argms["type"] = 7;
            ob.in.argms["idpj"] = self.idpj;
            ob.in.argms["path"] = self.pjpath;
            ob.in.argms["idroi"] = self.selectroids;
            ob.in.argms["idmodelversion"] = "001";
            ob.in.argms["idmodel"] = gelem('idmodel').value;

            
            //console.log("self.selectroids", self.selectroids);
            ob.event = function () {
                console.log("this.ou[response]", this.ou["response"]);
                //DRW.setlabel(this.ou["response"]);
                self.labels = this.ou["response"]["labels"];
                self.labels = {"0":"non-pleura", "1":"pleura"};
                self.ypredicted = this.ou["response"]["yp"];
                colors = ["#ff0000", "#00ff00"]
                for (i in self.selectroids){
                    console.log("i", i);
                    idreg = self.selectroids[i];

                    lab = self.ypredicted[i];
                    console.log("lasdfasdççç",self.labels[lab], colors[lab]);
                    DRW.highlight_id(idreg,colors[lab]);
                }


            };
            ob.start();
        }
    };


    this.openproject = function (idpj) {
        /* self.pjpath = path;
        self.idpj = idpj;
        var ob = new ServiceData("make classification");
        ob.in.argms["type"] = 9;
        ob.in.argms["idpj"] = idpj;
        ob.event = function () {
            console.log(this.ou);
            //DRW.setlabel(this.ou["response"]);
            dpj = this.ou["response"][0]
            gelem("idnameproject").innerHTML = dpj["name"];
            txtnamedb = dpj["name"]+`&nbsp;<i class="fas fa-edit fa-sm"></i>`;
            gelem('iddatasettitle').innerHTML = txtnamedb;            
            console.log("selflung.data", dpj);            

            DRW.chosseimage(path, dpj);

        };
        ob.start(); */

        datax = {
            "lwidth":700,
            "umax":0.96,
            "pcolor":[],
            "umin":0.1,
            "targetsnames":["class1","class2","class3"],
            "instvertexratio":5,
            "instvertexoacity":1.0,
            "idinstancelabel":["lab1","lab2","lab3","lab4","lab5","lab6","lab7","lab8","lab9","lab10"],
            "points":[
                {"x":4,"y":14,"t":0,"u":0.1},
                {"x":43,"y":1,"t":1,"u":0.6},
                {"x":14,"y":12,"t":2,"u":0.3},
                {"x":24,"y":18,"t":1,"u":0.6},
                {"x":22,"y":3,"t":2,"u":0.76},
                {"x":2,"y":10,"t":3,"u":0.46},
                {"x":26,"y":8,"t":4,"u":0.96},
                {"x":29,"y":9,"t":5,"u":0.69},
            ],
            "edges":[
                { "source": 0,"target": 1,"weight": 0.5},
                { "source": 2,"target": 3,"weight": 0.5},
                { "source": 0,"target": 2,"weight": 0.5},
                { "source": 1,"target": 3,"weight": 0.5},
                { "source": 3,"target": 6,"weight": 0.5},
                { "source": 4,"target": 7,"weight": 0.5},
            ]    
        };
        self.data = datax;
    };
    
    this.selectbythreshold = function(T){
        //console.log("T",T);
        points = self.data.points;
        umin = self.data.umin;
        umax = self.data.umax;
        //console.log("xssda",points, umin, umax);
        sel = []
        for (i in points){
            //console.log("iiiiii",i);
            du = points[i]["u"];
            u = (du-umin)/(umax-umin);
            //console.log("uuuuuu",u);
            if (u>=T){
                sel.push(i);
            }
        }
        
        self.layoutprojection.highlight(sel);
    };
    
    /* this.changecolorstable = function (c) {
        if(self.colorstableshitttype==1){
            CCTT.id = c;
            VertexColorF = CCTT.interpolate();

            chart_palettecolors(self.layoutfeatures.selectbythreshold,
                "seq1", 20, self.lwidth-20, VertexColorF);

            self.layoutfeatures.vertexcolorf = VertexColorF;
            self.layoutfeatures.updatecolors();
        }
        else if(self.colorstableshitttype==2){
            CCTT.id = c;
            EdgeColorF = CCTT.interpolate();
            chart_histogram(self.setToolpiltex,
                self.hideToolpiltex,
                self.layoutfeatures.updatelinkoption,
                "seqedgehist", self.lwidth, EdgeColorF, self.datagff.layoutfeature["edgehist"]);

            self.layoutfeatures.edgecolorf = EdgeColorF;
            self.layoutfeatures.drawedges();
        }
        else if(self.colorstableshitttype==3){
            CCTT.id = c;
            ProjectionColorF = CCTT.interpolate();

            self.layoutinstance.projectioncolorf = ProjectionColorF;
            self.layoutinstance.updatecolors();
        }
    }; */
    
    this.setColorVertex = function(c){
        self.VertexColorF = c;
        
        console.log("self.VertexColorF XX", self.VertexColorF, c);
        chart_palettecolors(self.selectbythreshold,
            "seq1", 20, 250, self.VertexColorF);
        
        self.layoutprojection.updateColorVertex(self.VertexColorF);
    };

/*     this.setColorVertexThreshold = function(c){
        self.VertexColorF = c;
        chart_palettecolors(self.selectbythreshold,
            "seq1", 20, 250, self.VertexColorF);
        
        self.layoutprojection.updateColorVertex(self.VertexColorF);
    };
 */

    this.ex_semiautomatic = function(cx, cy){
        let ob = new ServiceData("semi-automatic segmentation");
        ob.in.argms["type"] = 3;
        ob.in.argms["cx"] = cx;
        ob.in.argms["cy"] = cy;

        ob.event = function () {
            //datax = this.ou["response"];
            self.contours = this.ou["response"]["macula"];
            self.targets = this.ou["response"]["targets"];
            console.log("self.contours", self.contours);
            DRW.draw_macula();

        };
        
        ob.start();        
    };

    
    this.main = function(){
        self.mw.main();
        CCTT.main();
        self.showlayout("openproject");  

        CCTT.id = "oranges";
        console.log("CCTT.id", CCTT.id);
        SCB.VertexColorF = CCTT.interpolate();
        
        console.log("self.VertexColorF", self.VertexColorF);

        /* chart_palettecolors(self.selectbythreshold,
            "seq1", 20, 250, self.VertexColorF); */
        



        self.openproject("id3kxk");
        path = "2022/06/5555sda5sd";
        dpj = {"width":1024,"height":1024};
        DRW.chosseimage(path, dpj);

        /* self.layoutprojection = new plotProjection(
            self.VertexColorF, "#lyimgview",
            self.setToolpiltexParc, self.hideToolpiltex, self.data); */
    };
    //this.opengallery();
    //this.showlayout("gallerylist");  

    //updatesizeandopacity
}

function openprojects() {
    //self.fullScreen();
    SCB.opengallery();
    SCB.showlayout('gallerylist');

}
function mwalert(title, txtbody) {
    //self.fullScreen();
    SCB.mw.alert(title, txtbody);
}

