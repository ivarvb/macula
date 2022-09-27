/*
# Author: Ivar Vargas Belizario
# Copyright (c) 2020
# E-mail: ivar@usp.br
*/


function hidewindowinfo() {
    //    gelem('idinfosoundfile').style.display = "none";
    //    mySoundSC.pause();
}



// from https://github.com/substack/point-in-polygon
function pointInPolygon(point, vs) {
    var xi, xj, i, intersect,
        x = point[0],
        y = point[1],
        inside = false;
    for (var i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        xi = vs[i][0],
            yi = vs[i][1],
            xj = vs[j][0],
            yj = vs[j][1],
            intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function polygonToPath(polygon) {
    return ("M" + (polygon.map(function (d) { return d.join(','); }).join('L')));
}











function plotProjection(fnc_VColorF, idview, fnc_setToolpiltex, fnc_hideToolpiltex, datax) {

    var self = this;
    var data = datax.points;
    var edges = datax.edges;

    var margin = { top: 0, right: 0, bottom: 0, left: 0 },
        width = datax.lwidth,
        height = datax.lwidth;

    // setup x
    var xValue = function (d) { return d.x; }, // data -> value
        xScale = d3.scaleLinear().range([0, width]), // value -> display
        xMap = function (d) { return xScale(xValue(d)); }, // data -> display
        //        xAxis = d3.svg.axis().scale(xScale).orient("bottom");
        xAxis = d3.axisBottom(xScale);

    // setup y
    var yValue = function (d) { return d.y; }, // data -> value
        yScale = d3.scaleLinear().range([height, 0]), // value -> display
        yMap = function (d) { return yScale(yValue(d)); }, // data -> display
        yAxis = d3.axisLeft(yScale);


    xScale.domain([d3.min(data, xValue) - 5, d3.max(data, xValue) + 5]);
    yScale.domain([d3.min(data, yValue) - 5, d3.max(data, yValue) + 5]);

    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    
    this.selected = [];
    this.transform = d3.zoomIdentity;
    this.keycommand = 0;    
    this.isdragdrawing = false;
    
    var lassoPolygon;
    var lassoPath;
    var closePath;

    var drag = d3.drag()
        .on("start", function () {
            switch(self.keycommand){
                case 0:
                    self.isdragdrawing = true;
                    lassoPolygon = [d3.mouse(this)];
                    if (lassoPath) {
                        lassoPath.remove();
                    }
                    lassoPath = self.svg
                        .append('path')
                        .attr('fill', '#0bb')
                        .attr('fill-opacity', 0.1)
                        .attr('stroke', '#0bb')
                        .attr('stroke-dasharray', '3, 3');
                    closePath = self.svg
                        .append('line')
                        .attr('x2', lassoPolygon[0][0])
                        .attr('y2', lassoPolygon[0][1])
                        .attr('stroke', '#0bb')
                        .attr('stroke-dasharray', '3, 3')
                        .attr('opacity', 0);
                    break;
            }
        })
        .on("drag", function () {
            switch(self.keycommand){
                case 0:
                    self.isdragdrawing = true;
                    if (lassoPath != null){                    
                        var point = d3.mouse(this);
                        lassoPolygon.push(point);
                        lassoPath.attr('d', polygonToPath(lassoPolygon));
                        closePath
                            .attr('x1', point[0])
                            .attr('y1', point[1])
                            .attr('opacity', 1);
                    }
                    break;
                case 1:
                    self.dragmove();
                    break;
            }
        })
        .on("end", function () {
            switch(self.keycommand){
                case 0:
                    if (lassoPath != null){
                        closePath.remove();
                        closePath = null;
                        lassoPath.attr('d', polygonToPath(lassoPolygon) + 'Z');
                        self.selected = [];
                        self.container.selectAll(".dot").each(function (d, i) {
                            // var xx = (parseFloat(d3.select(this).attr("cx")) * savedScale) + savedTranslation[0];
                            // var yy = (parseFloat(d3.select(this).attr("cy")) * savedScale) + savedTranslation[1];

                            var xx = (parseFloat(d3.select(this).attr("cx")) * self.transform.k) + self.transform.x;
                            var yy = (parseFloat(d3.select(this).attr("cy")) * self.transform.k) + self.transform.y;

                            point = [xx, yy];
                            if (pointInPolygon(point, lassoPolygon)) {
                                self.selected.push(i);
                            }
                        });
                        self.highlight(self.selected);
                        //gelem(argms["infright"]).innerHTML = " / SELECTED: " + self.selected.length;
                        lassoPath.remove();
                        lassoPath = null;
                        lassoPolygon = null;
                    }
                    self.isdragdrawing = false;
                    break;
            }
        });

    var zoom = d3.zoom()
        .scaleExtent([0.5, 50])
        .on("zoom", function () {
            self.transform = d3.event.transform;
            self.container.attr("transform", self.transform);
        });

    d3.select(idview).selectAll("svg").remove();
    this.svg = d3.select(idview)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .call(drag)
        .call(zoom)
        .append("g");
    //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    this.container = this.svg.append("g");


    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    
    /////////////////////////////////////////////////////////    

    var sizexy = datax.instvertexratio;
    var sizebr = 1.75;

    self.links = self.container.append("g").selectAll('path');
    self.nodes = self.container.append("g").selectAll(".dot");

   
    self.nodes = self.nodes.data(data);
    self.nodes.exit().remove();
    self.nodes = self.nodes.enter().append("circle")
        .attr("class", "dot")
        .attr("r", sizexy)
        .attr("cx", xMap)
        .attr("cy", yMap)
        .style("opacity", datax.instvertexoacity)
        .style('stroke', 'white')
        .style('stroke-width', sizebr)
        .style("fill", function (d) {
            //return self.projectioncolorf(d.t/(targetsize)); 
            return fnc_VColorF((d.u-datax.umin)/(datax.umax-datax.umin));
            })
        .on("mouseover", function (d,i) {
            fnc_setToolpiltex(
                d3.event.pageX,
                d3.event.pageY,
                i
                );
        })
        .on("mouseout", function (d) {
            fnc_hideToolpiltex();
        })
        .merge(self.nodes);


    self.d3line = d3.line()
        .x(function (d) { return d.x; })
        .y(function (d) { return d.y; });

    //xynodex = self.nodesc.nodes();
   
    /* edges */        
    self.links = self.links.data(edges);
    self.links.exit().remove();
    self.links = self.links.enter()
                .append('path')
                .attr('d', function(d) {
                        a = d3.select(self.nodes.nodes()[d.source]);
                        b = d3.select(self.nodes.nodes()[d.target]);
                    
                        acx = a.attr("cx");
                        acy = a.attr("cy");
                        bcx = b.attr("cx");
                        bcy = b.attr("cy");
                        //console.log("ss", d3.select(ss[0]).attr("cy"))
                        return 'M '+acx+' '+acy+' L '+ bcx +' '+bcy
                    },                
                )
                .style('stroke', 'black')
                .style("stroke-opacity", 1.0)
                .style("stroke-width", 0.5);


    this.highlight = function (ids) {
        self.svg.selectAll("circle")
        //d3.select(view).selectAll("circle")
            .attr("r", datax.instvertexratio)
            .style("opacity", datax.instvertexoacity)
            .style("stroke", "white");

        //var selectionBArray = d3.select(view).selectAll("dot").nodes();
        //var selectionBArray = d3.select(view).selectAll("circle").nodes();
        var selectionBArray = self.svg.selectAll(".dot")["_groups"][0];
        //console.log("selectionBArray", selectionBArray, ids,"s");
        for (var i in ids) {
            cir = selectionBArray[ids[i]];
            //console.log("cir", cir);
            cir.style.stroke = d3.color(cir.style.fill).darker();
            //cir.style.stroke = "#94f7f4";
        }
    };

    this.updatesizeandopacity = function () {
        d3.select(idview).selectAll("circle")
        .attr("r", datax.instvertexratio)
        .style("opacity", datax.instvertexoacity);
    };

    this.updateColorVertex = function (fnc_ColorF) {    
        var selectionBArray = self.svg.selectAll(".dot")["_groups"][0];       
        self.nodes
            .style("fill", function (d) {
                //return self.projectioncolorf(d.t/(targetsize));
                return fnc_ColorF((d.u-datax.umin)/(datax.umax-datax.umin));                
            })
            .style("stroke", function (d) {
                return "#fff";
            });

        for (var i in self.selected) {
            cir = selectionBArray[self.selected[i]];
            cir.style.stroke = d3.color(cir.style.fill).darker();
            //cir.style.strokeWidth = 2.25;
            cir.style.opacity = "1.0";
        }

    };
    self.dragmove = function() {
        self.transform.x = self.transform.x+d3.event.dx;
        self.transform.y = self.transform.y+d3.event.dy;
        self.container.attr("transform", self.transform);
        //self.segments.attr("transform", self.transform);
    }

    document.addEventListener('keydown', (event) => {
        if(!self.isdragdrawing){
            if (event.altKey){
                self.keycommand = 1;
                d3.select("body").style("cursor", "move")
            }   
        }
    });
    document.addEventListener('keyup', (event) => {
        self.keycommand = 0;
        d3.select("body").style("cursor", "default")
    });

}

