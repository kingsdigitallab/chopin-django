from . import imagetools

__author__ = 'Elliot'
from .models import *
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from django.db import connection


def mergeBarNumbers():
    cursor = connection.cursor()
    for x in range(0, 1500):
        bars = Bar.objects.filter(barlabel=x).order_by('id')
        master = None
        if bars.count() > 0:
            # First bar
            master = bars[0]
        for b in bars:
            if b != master:
                sql = "update ocve_bar_barregion set bar_id=" + \
                    str(master.id) + " where bar_id=" + str(b.id)
                cursor.execute(sql)
                sql = "update ocve_barspine set bar_id=" + \
                    str(master.id) + " where bar_id=" + str(b.id)
                cursor.execute(sql)
                b.delete()


# Convert barregions to geoJSON coordinates
def toGeos(regions, version):
    geos = []
    w = regions[0].pageimage.width
    h = regions[0].pageimage.height
    for br in regions:
        if br.y > 0:
            g = BarRegionGeo(br, 1, 1, w, h, version)
            geos.append(g)
    return geos


# Corrects the incorrect bar regions coordinates cause by moving
# from cropped to uncropped page images between phases
# id=page id
def correctCropping(id, offsetX, offsetY):
    regions = barRegionsByPageImage(id)
    for r in regions:
        h = regions[0].pageimage.height
        r.x = (r.x + offsetX)
        r.y = (r.y + offsetY)
        r.save()


def barRegionsByPageImage(Id):
    regions = BarRegion.objects.filter(
        pageimage__id=Id).filter(
        bar__barnumber__gte=0).distinct()
    regions = sorted(regions, key=lambda region: region.getLowestBarNumber())
    return regions


def barRegionsByPage(Id):
    regions = BarRegion.objects.filter(page__id=Id).order_by('bar')
    return regions


def pagesBySource(sourceId):
    pages = Page.objects.filter(sourcecomponent__source__id=sourceId)
    return pages


def getGeoJSON(id, version):
    # pageID=request.POST['pageId']
    pageimage = PageImage.objects.get(id=id)
    l = PageLegacy.objects.get(pageimage=pageimage)
    regions = barRegionsByPageImage(int(id))
    if len(regions) > 0:
        geos = toGeos(regions, version)
        return geos
    return None


def getViewInPageJSON(id, barid):
    # pageID=request.POST['pageId']
    pageimage = PageImage.objects.get(id=id)
    l = PageLegacy.objects.get(pageimage=pageimage)
    regions = barRegionsByPageImage(int(id))
    # regions = regions.filter(pk=barid)

    regions = [r for r in regions if r.id == int(barid)]

    if len(regions) > 0:
        geos = toGeos(regions, "OL3")
        return geos
    return None


# Use a JSON feature from Openlayers vector layer to insert/update
# bar region
# f=jsonfeature,pi=PageImage
def updateBarRegionFromFeature(br, f):
    try:

        pageHeight = br.pageimage.height
        geometry = f['geometry']['coordinates']
        # Transform geoJSON back to x,y,width,height
        br.x = geometry[0][1][0]
        br.y = pageHeight - geometry[0][1][1]
        br.width = geometry[0][3][0] - geometry[0][1][0]
        br.height = (geometry[0][1][1] - geometry[0][3][1])
        # Save
        br.save()
    except MultiValueDictKeyError:
        pass
    return ""


# Adapt coordinates to openlayers display
# reverse numbers for geography, as not starting at 0,0
class BarRegionGeo:

    def __init__(self, br, rx, ry, w, h, version):
        if version == "OL3":
            self.initOL3(br, rx, ry, w, h)
        elif version == "OL2":
            self.initOL2(br, rx, ry, w, h)

    # Adapt coordinates to openlayers display

    def initOL3(self, br, rx, ry, w, h):
        self.x1 = (br.x * rx)
        self.x2 = ((br.x + br.width) * rx)
        self.y1 = ((br.y + br.height) * ry) * -1
        self.y2 = (br.y * ry) * -1
        self.id = br.id
        self.anomaly = br.anomaly
        barid = ''
        for b in br.bar.all():
            if len(barid) > 0:
                barid += ', '
            if b.barnumber == 0:
                barid += 'zero'
            else:
                barid = barid + b.barlabel
            self.barid = b.id

        self.label = barid

    # For openlayers 2 (bar editor)
    def initOL2(self, br, rx, ry, w, h):
        self.x1 = (br.x * rx)
        self.x2 = ((br.x + br.width) * rx)
        self.y1 = h - ((br.y + br.height) * ry)
        self.y2 = h - (br.y * ry)
        # self.y1 = ((br.y + br.height) * ry) * -1
        # self.y2 = (br.y * ry) * -1
        self.id = br.id
        self.anomaly = br.anomaly
        barid = ''
        for b in br.bar.all():
            if len(barid) > 0:
                barid += ', '
            if b.barnumber == 0:
                barid += 'zero'
            else:
                barid = barid + b.barlabel
            self.barid = b.id

        self.label = barid


# Generate thumbnail from iip request#
# based on coordination information
# todo simplify
class BarRegionThumbnail:
    # def getURL(self):
    #     url= self.pi.getJP2Path()
    #     iipX = float(self.br.x) / self.pi.width
    #     iipY = float(self.br.y) / self.pi.height
    #     #Width and height in iip are percentages of total image
    #     iipWidth = float(self.br.width) / self.pi.width
    #     iipHeight = float(self.br.height) / self.pi.height
    #     params = "&cnt=1&QLT=100&WID=" + str(settings.THUMBNAIL_WIDTH)
    #     if self.br is not None and self.pi is not None:
    #         #todo shrink image first?
    #         params = params + "&RGN=" + str(iipX) + "," + str(iipY) + "," + str(iipWidth) + "," + str(
    #                 iipHeight) + "&CVT=JPG"
    #     else:
    #         return "Error"
    #     return url + params

    def iipParams(self, iipX, iipY, curWidth, curHeight, initialparams):
        # Width and height in iip are percentages of total image
        iipWidth = float(curWidth) / self.pi.width
        iipHeight = float(curHeight) / self.pi.height
        return initialparams + "&RGN=" + \
            str(iipX) + "," + str(iipY) + "," + str(iipWidth) + "," + str(iipHeight) + "&CVT=JPG"

    def getURL(self, initalparams):
        url = self.pi.getJP2Path()
        urls = []

        if self.range is not None:
            # Bar range, return multiple urls
            curWidth = 0
            curHeight = 0
            iipX = 0
            iipY = 0
            for r in self.range:
                if iipX == 0 and iipY == 0:
                    iipX = float(r.x) / self.pi.width
                    iipY = float(r.y) / self.pi.height
                    curWidth = r.width
                    curHeight = r.height

                elif curHeight == 0 or r.height - curHeight == 0:
                    # Same system, extend current url
                    curWidth += r.width
                else:
                    # System break, generate new url
                    urls.append(
                        url +
                        self.iipParams(
                            iipX,
                            iipY,
                            curWidth,
                            curHeight,
                            initalparams))
                    iipX = float(r.x) / self.pi.width
                    iipY = float(r.y) / self.pi.height
                    curWidth = r.width
                    curHeight = r.height
                    url = r.pageimage.getJP2Path()

            if curWidth > 0:
                urls.append(
                    url +
                    self.iipParams(
                        iipX,
                        iipY,
                        curWidth,
                        curHeight,
                        initalparams))
        else:
            # Single range
            # Convert coordinates to image percentages
            iipX = float(self.br.x) / self.pi.width
            iipY = float(self.br.y) / self.pi.height
            if self.br is not None and self.pi is not None:
                # todo shrink image first?
                params = self.iipParams(
                    iipX, iipY, self.br.width, self.br.height, initalparams)
            else:
                return "Error"
            urls.append(url + params)
        return urls

    def getBarImageURL(self):
        return self.getURL("&hei=" +
                           str(settings.BAR_IMAGE_HEIGHT) +
                           "&cnt=1&QLT=100")

    def getLargeURL(self):
        return self.getURL("&cnt=1&QLT=100")

    def getSource(self):
        return Source.objects.filter(
            sourcecomponent__page__pageimage__barregion=self.br).distinct()[0]

    def __init__(self, br, page, pi, range=None):
        self.br = br
        self.page = page
        self.pi = pi
        if self.br.annotation.count() > 0:
            self.annotation = 1
        else:
            self.annotation = 0

        if range is not None and len(range) > 0:
            self.range = range
        else:
            self.range = None

            # Checking for bars split across systems, add them to the range
            if Bar.objects.filter(
                    barregion=self.br,
                    barlabel__contains='i').exists():
                extraRegions = BarRegion.objects.filter(
                    bar__barnumber=self.br.getLowestBarNumber(),
                    pageimage=self.br.pageimage)
                if self.range is not None:
                    concatlist = list(extraRegions) + list(self.range[1:])
                    self.range = concatlist
                else:
                    self.range = extraRegions

        if self.range is not None:
            self.regionlabel = "bs " + \
                str(self.br) + '\u2013' + str(self.range.last())
        else:
            self.regionlabel = "b. " + str(self.br)
            # self.URL = self.getURL()
