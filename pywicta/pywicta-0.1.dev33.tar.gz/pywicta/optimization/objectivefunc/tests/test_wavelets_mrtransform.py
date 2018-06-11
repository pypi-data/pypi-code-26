from pywicta.optimization.objectivefunc.wavelets_mrtransform import ObjectiveFunction

def test_str():
    """Test the ObjectiveFunction to string conversion."""

    func = ObjectiveFunction(input_files=".",
                             cam_id="LSTCam",
                             optimization_metric="mse",
                             max_num_img=10,
                             aggregation_method="mean",
                             num_scales=3,
                             type_of_filtering="cluster_filtering",
                             last_scale_treatment="mask",
                             detect_only_positive_structures=False,
                             kill_isolated_pixels=False,
                             noise_distribution=None,
                             tmp_files_directory=None,
                             cleaning_failure_score=float('inf'))

    expected_str = "wavelet_mrtransform_3-scales_" \
                   "cluster-filtering_mask_pos-and-neg_no-kill_" \
                   "failure-inf_agg-mean_metric-mse"

    assert str(func) == expected_str