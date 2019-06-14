# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

""" MiBIG specific sideloading """

import json
from typing import Any, Dict, List

from antismash.common.module_results import DetectionResults
from antismash.common.secmet import CDSFeature, Protocluster, Record
from antismash.common.secmet.locations import FeatureLocation, CompoundLocation


class MibigAnnotations(DetectionResults):
    def __init__(self, record_id: str) -> None:
        super().__init__(record_id)
        self.clusters = []
        self.data = {}

    def get_predicted_protoclusters(self) -> List[Protocluster]:
        return self.clusters

    def to_json(self) -> Dict[str, Any]:
        return {}


def mibig_loader(annotations_file: str, record: Record) -> MibigAnnotations:
    with open(annotations_file) as handle:
        annotations = json.load(handle)
    results = MibigAnnotations(record.id)

    # set and append region
    product = ", ".join(annotations["cluster"]["biosyn_class"])
    loci = annotations["cluster"]["loci"]
    assert loci["accession"] == record.id
    start = loci.get("start_coord", 1) - 1
    end = loci.get("end_coord", len(record.seq))
    cluster = Protocluster(FeatureLocation(start, end), FeatureLocation(start, end),
                           tool="mibig", cutoff=-1,
                           neighbourhood_range=0, product=product,
                           detection_rule="")
    results.clusters.append(cluster)

    if "genes" in annotations["cluster"]:
        # append new CDSes from annotation
        for gene in annotations["cluster"]["genes"].get("extra_genes", []):
            if "id" in gene and "location" in gene:
                # todo: check if exist in gbk
                exons = [FeatureLocation(exon["start"] - 1, exon["end"], strand=gene["location"]["strand"]) for exon in gene["location"]["exons"]]
                location = CompoundLocation(exons) if len(exons) > 1 else exons[0]
                translation = gene.get("translation", "") # what to do if no translation available?
                cds_feature = CDSFeature(location=location, locus_tag=gene["id"], translation=translation)
                record.add_cds_feature(cds_feature)

        # re-annotate CDSes
        for cds_feature in record.get_cds_features_within_location(cluster.location):
            locus_tag = cds_feature.locus_tag
            protein_id = cds_feature.protein_id
            name = cds_feature.gene
            for annot in annotations["cluster"]["genes"].get("annotations", []):
                if locus_tag and annot["id"] == locus_tag:
                    pass
                elif protein_id and annot["id"] == protein_id:
                    pass
                elif name and annot.get("name", None) == name:
                    pass
                else:
                    continue
                if "product" in annot:
                    cds_feature.product = annot["product"]

    # store raw data for downstream processing
    results.data = annotations

    return results