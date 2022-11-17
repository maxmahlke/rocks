#!/usr/bin/env python


import rocks
import unittest


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Test identification
class ssoCard_identification_parameters(unittest.TestCase):
    # --------------------------------------------------------------------------------
    # Test Number with Berthier
    def test_identification_number(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.number,
            int,
            msg="Wrong class for the number"
        )
        self.assertEqual(
            ssocard.number,
            15905,
            msg="Wrong value for number"
        )

    # Test Name with Berthier
    def test_identification_name(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.name,
            str,
            msg="Wrong class for the name"
        )
        self.assertEqual(
            ssocard.name,
            "Berthier",
            msg="Wrong value for name"
        )

    # Test ID with Berthier
    def test_identification_id(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.id_,
            str,
            msg="Wrong class for the id"
        )
        self.assertEqual(
            ssocard.id_,
            "Berthier",
            msg="Wrong value for id"
        )

    # Test type with Berthier
    def test_identification_id(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.type_,
            str,
            msg="Wrong class for the type"
        )
        self.assertEqual(
            ssocard.type_,
            "Asteroid",
            msg="Wrong value for type"
        )

    # Test Dynamical class with Berthier
    def test_identification_class(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.class_,
            str,
            msg="Wrong class for the dynamical class"
        )
        self.assertEqual(
            ssocard.class_,
            "MB>Middle",
            msg="Wrong value for dynamical class"
        )

    # Test parent with Berthier
    def test_identification_id(self):
        ssocard = rocks.Rock("Berthier")
        self.assertIsInstance(
            ssocard.parent,
            str,
            msg="Wrong class for the parent"
        )
        self.assertEqual(
            ssocard.parent,
            "Sun",
            msg="Wrong value for parent"
        )



# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Test dynamical properties: Osculating elements
class ssoCard_osculating_parameters(unittest.TestCase):
    # --------------------------------------------------------------------------------
    # Test osculating elements biblio with Pluto
    def test_osculating_biblio(self):
        ssocard = rocks.Rock("Pluto")
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref,
            list,
            msg="Wrong class for the orbital_elements bibref",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref[0].doi,
            str,
            msg="Wrong class for the orbital_elements bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref[0].year,
            int,
            msg="Wrong class for the orbital_elements bibref - year",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref[0].title,
            str,
            msg="Wrong class for the orbital_elements bibref - title",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref[0].bibcode,
            str,
            msg="Wrong class for the orbital_elements bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.bibref[0].shortbib,
            str,
            msg="Wrong class for the orbital_elements bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test semi-major axis with Pluto
    def test_osculating_semi_major_axis_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.semi_major_axis.value,
            39.708,
            delta=0.001,
            msg="Wrong value for osculating element: semi-major axis",
        )

    def test_osculating_semi_major_axis_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.semi_major_axis.error.min_,
            -1e-8,
            delta=1e-8,
            msg="Wrong value for osculating semi-major axis lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.semi_major_axis.error.max_,
            1e-8,
            delta=1e-8,
            msg="Wrong value for osculating semi-major axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test eccentricity with Pluto
    def test_osculating_eccentricity_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.eccentricity.value,
            0.249,
            delta=0.001,
            msg="Wrong value for osculating element: eccentricity",
        )

    def test_osculating_eccentricity_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.eccentricity.error.min_,
            -1e-8,
            delta=1e-8,
            msg="Wrong value for osculating eccentricity lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.eccentricity.error.max_,
            1e-8,
            delta=1e-8,
            msg="Wrong value for osculating eccentricity axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test inclination with Pluto
    def test_osculating_inclination_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.inclination.value,
            17.11,
            delta=0.01,
            msg="Wrong value for osculating element: inclination",
        )

    def test_osculating_inclination_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.inclination.error.min_,
            -1e-6,
            delta=1e-6,
            msg="Wrong value for osculating inclination lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.inclination.error.max_,
            1e-6,
            delta=1e-6,
            msg="Wrong value for osculating inclination axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test node_longitude with Pluto
    def test_osculating_node_longitude_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.node_longitude.value,
            110.30,
            delta=0.01,
            msg="Wrong value for osculating element: node_longitude",
        )

    def test_osculating_node_longitude_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.node_longitude.error.min_,
            -1e-5,
            delta=1e-5,
            msg="Wrong value for osculating node_longitude lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.node_longitude.error.max_,
            1e-5,
            delta=1e-5,
            msg="Wrong value for osculating node_longitude axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test perihelion_argument with Pluto
    def test_osculating_perihelion_argument_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.perihelion_argument.value,
            115.11,
            delta=0.01,
            msg="Wrong value for osculating element: perihelion_argument",
        )

    def test_osculating_perihelion_argument_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.perihelion_argument.error.min_,
            -1e-6,
            delta=1e-6,
            msg="Wrong value for osculating perihelion_argument lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.perihelion_argument.error.max_,
            1e-6,
            delta=1e-6,
            msg="Wrong value for osculating perihelion_argument axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test mean_motion with Pluto
    def test_osculating_mean_motion_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_motion.value,
            0.00393889,
            delta=0.0001,
            msg="Wrong value for osculating element: mean_motion",
        )

    def test_osculating_mean_motion_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_motion.error.min_,
            -1e-8,
            delta=1e-8,
            msg="Wrong value for osculating mean_motion lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_motion.error.max_,
            1e-8,
            delta=1e-8,
            msg="Wrong value for osculating mean_motion axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test orbital_period with Pluto
    def test_osculating_orbital_period_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.orbital_period.value,
            91396.201046,
            delta=0.00001,
            msg="Wrong value for osculating element: orbital_period",
        )

    def test_osculating_orbital_period_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.orbital_period.error.min_,
            -1e-8,
            delta=1e-8,
            msg="Wrong value for osculating orbital_period lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.orbital_period.error.max_,
            1e-8,
            delta=1e-8,
            msg="Wrong value for osculating orbital_period axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test mean_anomaly with Pluto
    def test_osculating_mean_anomaly_value(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_anomaly.value,
            46.19,
            delta=0.01,
            msg="Wrong value for osculating element: mean_anomaly",
        )

    def test_osculating_mean_anomaly_errors(self):
        ssocard = rocks.Rock("Pluto")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_anomaly.error.min_,
            -1e-6,
            delta=1e-6,
            msg="Wrong value for osculating mean_anomaly lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.mean_anomaly.error.max_,
            1e-6,
            delta=1e-6,
            msg="Wrong value for osculating mean_anomaly axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test CEU with Juno
    def test_osculating_ceu_value(self):
        ssocard = rocks.Rock("Juno")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu.value,
            0.015,
            delta=0.002,
            msg="Wrong value for osculating element: CEU",
        )

    def test_osculating_ceu_errors(self):
        ssocard = rocks.Rock("Juno")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu.error.min_,
            -0.001,
            delta=0.001,
            msg="Wrong value for osculating CEU lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu.error.max_,
            0.001,
            delta=0.001,
            msg="Wrong value for osculating CEU axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test CEU rate with Juno
    def test_osculating_ceu_rate_value(self):
        ssocard = rocks.Rock("Juno")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu_rate.value,
            0.0001,
            delta=0.0001,
            msg="Wrong value for osculating element: CEU rate",
        )

    def test_osculating_ceu_rate_errors(self):
        ssocard = rocks.Rock("Juno")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu_rate.error.min_,
            -0.0001,
            delta=0.0001,
            msg="Wrong value for osculating CEU rate lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.orbital_elements.ceu_rate.error.max_,
            0.0001,
            delta=0.0001,
            msg="Wrong value for osculating CEU rate axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test ancillary information with Pallas
    def test_osculating_author(self):
        ssocard = rocks.Rock("Pallas")
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.author,
            str,
            msg="Wrong class for the osculating elements - author",
        )

    def test_osculating_number_observation(self):
        ssocard = rocks.Rock("Pallas")
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.number_observation,
            int,
            msg="Wrong class for the osculating elements - number_observation",
        )

    def test_osculating_orbital_arc(self):
        ssocard = rocks.Rock("Pallas")
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.orbital_arc,
            int,
            msg="Wrong class for the osculating elements - orbital_arc",
        )

    def test_osculating_ref_epoch(self):
        ssocard = rocks.Rock("Pallas")
        self.assertIsInstance(
            ssocard.parameters.dynamical.orbital_elements.ref_epoch,
            float,
            msg="Wrong class for the osculating elements - ref_epoch",
        )


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Test dynamical properties: Proper elements
class ssoCard_proper_parameters(unittest.TestCase):
    # --------------------------------------------------------------------------------
    # Test proper elements biblio with Hebe
    def test_proper_biblio(self):
        ssocard = rocks.Rock("Hebe")
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref,
            list,
            msg="Wrong class for the proper_elements bibref",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref[0].doi,
            str,
            msg="Wrong class for the proper_elements bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref[0].year,
            int,
            msg="Wrong class for the proper_elements bibref - year",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref[0].title,
            str,
            msg="Wrong class for the proper_elements bibref - title",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref[0].bibcode,
            str,
            msg="Wrong class for the proper_elements bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.parameters.dynamical.proper_elements.bibref[0].shortbib,
            str,
            msg="Wrong class for the proper_elements bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test proper semi-major axis with Hebe
    def test_proper_semi_major_axis_value(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_semi_major_axis.value,
            2.425,
            delta=0.001,
            msg="Wrong value for proper element: semi-major axis",
        )

    def test_proper_semi_major_axis_errors(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_semi_major_axis.error.min_,
            -2.1e-6,
            delta=1e-7,
            msg="Wrong value for proper semi-major axis lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_semi_major_axis.error.max_,
            2.1e-6,
            delta=1e-7,
            msg="Wrong value for proper semi-major axis upper error",
        )

    # --------------------------------------------------------------------------------
    # Test proper eccentricity axis with Hebe
    def test_proper_eccentricity_value(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_eccentricity.value,
            0.1588,
            delta=0.0001,
            msg="Wrong value for proper element: eccentricity",
        )

    def test_proper_eccentricity_errors(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_eccentricity.error.min_,
            -2.1e-4,
            delta=1e-5,
            msg="Wrong value for proper eccentricity lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_eccentricity.error.max_,
            2.1e-4,
            delta=1e-5,
            msg="Wrong value for proper eccentricity upper error",
        )

    # --------------------------------------------------------------------------------
    # Test proper inclination axis with Hebe
    def test_proper_inclination_value(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_inclination.value,
            14.406,
            delta=0.001,
            msg="Wrong value for proper element: inclination",
        )

    def test_proper_inclination_errors(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_inclination.error.min_,
            -2.2e-2,
            delta=1e-3,
            msg="Wrong value for proper inclination lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_inclination.error.max_,
            2.2e-2,
            delta=1e-3,
            msg="Wrong value for proper inclination upper error",
        )

    # --------------------------------------------------------------------------------
    # Test sine of proper inclination axis with Hebe
    def test_proper_sine_inclination_value(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_sine_inclination.value,
            0.2487,
            delta=0.001,
            msg="Wrong value for proper element: sine of inclination",
        )

    def test_proper_sine_inclination_errors(self):
        ssocard = rocks.Rock("Hebe")
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_sine_inclination.error.min_,
            -3.9e-4,
            delta=1e-5,
            msg="Wrong value for proper sine of inclination lower error",
        )
        self.assertAlmostEqual(
            ssocard.parameters.dynamical.proper_elements.proper_sine_inclination.error.max_,
            3.9e-4,
            delta=1e-5,
            msg="Wrong value for proper sine of inclination upper error",
        )



# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Test physical properties
class ssoCard_physical_parameters(unittest.TestCase):
    # --------------------------------------------------------------------------------
    # Test absolute magnitude using Eros
    def test_absolute_magnitude_value(self):
        ssocard = rocks.Rock("Eros")
        self.assertAlmostEqual(
            ssocard.absolute_magnitude.H.value,
            0.492,
            delta=0.010,
            msg="Wrong value for absolute_magnitude",
        )

    def test_absolute_magnitude_errors(self):
        ssocard = rocks.Rock("Eros")
        self.assertAlmostEqual(
            ssocard.absolute_magnitude.H.error.min_,
            -0.02,
            delta=0.01,
            msg="Wrong value for absolute_magnitude lower error",
        )
        self.assertAlmostEqual(
            ssocard.absolute_magnitude.H.error.max_,
            0.02,
            delta=0.01,
            msg="Wrong value for absolute_magnitude upper error",
        )

    def test_absolute_magnitude_biblio(self):
        ssocard = rocks.Rock("Eros")
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref,
            list,
            msg="Wrong class for the absolute_magnitude bibref",
        )
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref[0].doi,
            str,
            msg="Wrong class for the absolute_magnitude bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref[0].year,
            int,
            msg="Wrong class for the absolute_magnitude bibref - year",
        )
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref[0].title,
            str,
            msg="Wrong class for the absolute_magnitude bibref - title",
        )
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref[0].bibcode,
            str,
            msg="Wrong class for the absolute_magnitude bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.absolute_magnitude.bibref[0].shortbib,
            str,
            msg="Wrong class for the absolute_magnitude bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test diameter using Bennu
    def test_diameter_value(self):
        ssocard = rocks.Rock("Bennu")
        self.assertAlmostEqual(
            ssocard.diameter.value, 0.492, delta=0.010, msg="Wrong value for diameter"
        )

    def test_diameter_errors(self):
        ssocard = rocks.Rock("Bennu")
        self.assertAlmostEqual(
            ssocard.diameter.error.min_,
            -0.02,
            delta=0.01,
            msg="Wrong value for diameter lower error",
        )
        self.assertAlmostEqual(
            ssocard.diameter.error.max_,
            0.02,
            delta=0.01,
            msg="Wrong value for diameter upper error",
        )

    def test_diameter_method(self):
        ssocard = rocks.Rock("Bennu")
        self.assertIsInstance(
            ssocard.diameter.method, list, msg="Wrong class for the diameter method"
        )
        self.assertIsInstance(
            ssocard.diameter.method[0].doi,
            str,
            msg="Wrong class for the diameter method - DOI",
        )
        self.assertIsInstance(
            ssocard.diameter.method[0].year,
            int,
            msg="Wrong class for the diameter method - year",
        )
        self.assertIsInstance(
            ssocard.diameter.method[0].title,
            str,
            msg="Wrong class for the diameter method - title",
        )
        self.assertIsInstance(
            ssocard.diameter.method[0].bibcode,
            str,
            msg="Wrong class for the diameter method - bibcode",
        )
        self.assertIsInstance(
            ssocard.diameter.method[0].shortbib,
            str,
            msg="Wrong class for the diameter method - shortbib",
        )

    def test_diameter_biblio(self):
        ssocard = rocks.Rock("Bennu")
        self.assertIsInstance(
            ssocard.diameter.bibref, list, msg="Wrong class for the diameter bibref"
        )
        self.assertIsInstance(
            ssocard.diameter.bibref[0].doi,
            str,
            msg="Wrong class for the diameter bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.diameter.bibref[0].year,
            int,
            msg="Wrong class for the diameter bibref - year",
        )
        self.assertIsInstance(
            ssocard.diameter.bibref[0].title,
            str,
            msg="Wrong class for the diameter bibref - title",
        )
        self.assertIsInstance(
            ssocard.diameter.bibref[0].bibcode,
            str,
            msg="Wrong class for the diameter bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.diameter.bibref[0].shortbib,
            str,
            msg="Wrong class for the diameter bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test albedo using Vesta
    def test_albedo_value(self):
        ssocard = rocks.Rock("Vesta")
        self.assertAlmostEqual(
            ssocard.albedo.value, 0.38, delta=0.01, msg="Wrong value for albedo"
        )

    def test_albedo_errors(self):
        ssocard = rocks.Rock("Vesta")
        self.assertAlmostEqual(
            ssocard.albedo.error.min_,
            -0.04,
            delta=0.01,
            msg="Wrong value for albedo lower error",
        )
        self.assertAlmostEqual(
            ssocard.albedo.error.max_,
            0.04,
            delta=0.01,
            msg="Wrong value for albedo upper error",
        )

    def test_albedo_method(self):
        ssocard = rocks.Rock("Vesta")
        self.assertIsInstance(
            ssocard.albedo.method, list, msg="Wrong class for the albedo method"
        )
        self.assertIsInstance(
            ssocard.albedo.method[0].doi,
            str,
            msg="Wrong class for the albedo method - DOI",
        )
        self.assertIsInstance(
            ssocard.albedo.method[0].year,
            int,
            msg="Wrong class for the albedo method - year",
        )
        self.assertIsInstance(
            ssocard.albedo.method[0].title,
            str,
            msg="Wrong class for the albedo method - title",
        )
        self.assertIsInstance(
            ssocard.albedo.method[0].bibcode,
            str,
            msg="Wrong class for the albedo method - bibcode",
        )
        self.assertIsInstance(
            ssocard.albedo.method[0].shortbib,
            str,
            msg="Wrong class for the albedo method - shortbib",
        )

    def test_albedo_biblio(self):
        ssocard = rocks.Rock("Vesta")
        self.assertIsInstance(
            ssocard.albedo.bibref, list, msg="Wrong class for the albedo bibref"
        )
        self.assertIsInstance(
            ssocard.albedo.bibref[0].doi,
            str,
            msg="Wrong class for the albedo bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.albedo.bibref[0].year,
            int,
            msg="Wrong class for the albedo bibref - year",
        )
        self.assertIsInstance(
            ssocard.albedo.bibref[0].title,
            str,
            msg="Wrong class for the albedo bibref - title",
        )
        self.assertIsInstance(
            ssocard.albedo.bibref[0].bibcode,
            str,
            msg="Wrong class for the albedo bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.albedo.bibref[0].shortbib,
            str,
            msg="Wrong class for the albedo bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test mass using Ceres
    def test_mass_value(self):
        ssocard = rocks.Rock("Ceres")
        self.assertAlmostEqual(
            ssocard.mass.value, 9.384e20, delta=1e18, msg="Wrong value for mass"
        )

    def test_mass_errors(self):
        ssocard = rocks.Rock("Ceres")
        self.assertAlmostEqual(
            ssocard.mass.error.min_,
            -1e17,
            delta=1e17,
            msg="Wrong value for mass lower error",
        )
        self.assertAlmostEqual(
            ssocard.mass.error.max_,
            1e17,
            delta=1e17,
            msg="Wrong value for mass upper error",
        )

    def test_mass_method(self):
        ssocard = rocks.Rock("Ceres")
        self.assertIsInstance(
            ssocard.mass.method, list, msg="Wrong class for the mass method"
        )
        self.assertIsInstance(
            ssocard.mass.method[0].doi,
            str,
            msg="Wrong class for the mass method - DOI",
        )
        self.assertIsInstance(
            ssocard.mass.method[0].year,
            int,
            msg="Wrong class for the mass method - year",
        )
        self.assertIsInstance(
            ssocard.mass.method[0].title,
            str,
            msg="Wrong class for the mass method - title",
        )
        self.assertIsInstance(
            ssocard.mass.method[0].bibcode,
            str,
            msg="Wrong class for the mass method - bibcode",
        )
        self.assertIsInstance(
            ssocard.mass.method[0].shortbib,
            str,
            msg="Wrong class for the mass method - shortbib",
        )

    def test_mass_biblio(self):
        ssocard = rocks.Rock("Ceres")
        self.assertIsInstance(
            ssocard.mass.bibref, list, msg="Wrong class for the mass bibref"
        )
        self.assertIsInstance(
            ssocard.mass.bibref[0].doi,
            str,
            msg="Wrong class for the mass bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.mass.bibref[0].year,
            int,
            msg="Wrong class for the mass bibref - year",
        )
        self.assertIsInstance(
            ssocard.mass.bibref[0].title,
            str,
            msg="Wrong class for the mass bibref - title",
        )
        self.assertIsInstance(
            ssocard.mass.bibref[0].bibcode,
            str,
            msg="Wrong class for the mass bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.mass.bibref[0].shortbib,
            str,
            msg="Wrong class for the mass bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test density using Ryugu
    def test_density_value(self):
        ssocard = rocks.Rock("Ryugu")
        self.assertAlmostEqual(
            ssocard.density.value, 1305, delta=50, msg="Wrong value for density"
        )

    def test_density_errors(self):
        ssocard = rocks.Rock("Ryugu")
        self.assertAlmostEqual(
            ssocard.density.error.min_,
            -152,
            delta=10,
            msg="Wrong value for density lower error",
        )
        self.assertAlmostEqual(
            ssocard.density.error.max_,
            152,
            delta=10,
            msg="Wrong value for density upper error",
        )

    def test_density_method(self):
        ssocard = rocks.Rock("Ryugu")
        self.assertIsInstance(
            ssocard.density.method, list, msg="Wrong class for the density method"
        )
        self.assertIsInstance(
            ssocard.density.method[0].doi,
            str,
            msg="Wrong class for the density method - DOI",
        )
        self.assertIsInstance(
            ssocard.density.method[0].year,
            int,
            msg="Wrong class for the density method - year",
        )
        self.assertIsInstance(
            ssocard.density.method[0].title,
            str,
            msg="Wrong class for the density method - title",
        )
        self.assertIsInstance(
            ssocard.density.method[0].bibcode,
            str,
            msg="Wrong class for the density method - bibcode",
        )
        self.assertIsInstance(
            ssocard.density.method[0].shortbib,
            str,
            msg="Wrong class for the density method - shortbib",
        )

    def test_density_biblio(self):
        ssocard = rocks.Rock("Ryugu")
        self.assertIsInstance(
            ssocard.density.bibref, list, msg="Wrong class for the density bibref"
        )
        self.assertIsInstance(
            ssocard.density.bibref[0].doi,
            str,
            msg="Wrong class for the density bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.density.bibref[0].year,
            int,
            msg="Wrong class for the density bibref - year",
        )
        self.assertIsInstance(
            ssocard.density.bibref[0].title,
            str,
            msg="Wrong class for the density bibref - title",
        )
        self.assertIsInstance(
            ssocard.density.bibref[0].bibcode,
            str,
            msg="Wrong class for the density bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.density.bibref[0].shortbib,
            str,
            msg="Wrong class for the density bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test taxonomy using Lutetia
    def test_taxonomy_class_(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertEqual(
            ssocard.taxonomy.class_, "Xc", msg="Wrong value for taxonomy class"
        )

    def test_taxonomy_complex(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertEqual(
            ssocard.taxonomy.complex, "X", msg="Wrong value for taxonomy complex"
        )

    def test_taxonomy_technique(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertEqual(
            ssocard.taxonomy.technique, "Spec", msg="Wrong value for taxonomy technique"
        )

    def test_taxonomy_scheme(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertEqual(
            ssocard.taxonomy.scheme, "Bus-DeMeo", msg="Wrong value for taxonomy scheme"
        )

    def test_taxonomy_waverange(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertEqual(
            ssocard.taxonomy.waverange, "VISNIR", msg="Wrong value for taxonomy scheme"
        )

    def test_taxonomy_method(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertIsInstance(
            ssocard.taxonomy.method, list, msg="Wrong class for the taxonomy method"
        )
        self.assertIsInstance(
            ssocard.taxonomy.method[0].doi,
            str,
            msg="Wrong class for the taxonomy method - DOI",
        )
        self.assertIsInstance(
            ssocard.taxonomy.method[0].year,
            int,
            msg="Wrong class for the taxonomy method - year",
        )
        self.assertIsInstance(
            ssocard.taxonomy.method[0].title,
            str,
            msg="Wrong class for the taxonomy method - title",
        )
        self.assertIsInstance(
            ssocard.taxonomy.method[0].bibcode,
            str,
            msg="Wrong class for the taxonomy method - bibcode",
        )
        self.assertIsInstance(
            ssocard.taxonomy.method[0].shortbib,
            str,
            msg="Wrong class for the taxonomy method - shortbib",
        )

    def test_taxonomy_biblio(self):
        ssocard = rocks.Rock("Lutetia")
        self.assertIsInstance(
            ssocard.taxonomy.bibref, list, msg="Wrong class for the taxonomy bibref"
        )
        self.assertIsInstance(
            ssocard.taxonomy.bibref[0].doi,
            str,
            msg="Wrong class for the taxonomy bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.taxonomy.bibref[0].year,
            int,
            msg="Wrong class for the taxonomy bibref - year",
        )
        self.assertIsInstance(
            ssocard.taxonomy.bibref[0].title,
            str,
            msg="Wrong class for the taxonomy bibref - title",
        )
        self.assertIsInstance(
            ssocard.taxonomy.bibref[0].bibcode,
            str,
            msg="Wrong class for the taxonomy bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.taxonomy.bibref[0].shortbib,
            str,
            msg="Wrong class for the taxonomy bibref - shortbib",
        )

    # --------------------------------------------------------------------------------
    # Test thermal inertia using Steins
    def test_thermal_inertia_value(self):
        ssocard = rocks.Rock("Steins")
        self.assertAlmostEqual(
            ssocard.thermal_inertia.TI.value,
            200,
            delta=5,
            msg="Wrong value for thermal_inertia",
        )

    def test_thermal_inertia_errors(self):
        ssocard = rocks.Rock("Steins")
        self.assertAlmostEqual(
            ssocard.thermal_inertia.TI.error.min_,
            -99,
            delta=10,
            msg="Wrong value for thermal_inertia lower error",
        )
        self.assertAlmostEqual(
            ssocard.thermal_inertia.TI.error.max_,
            99,
            delta=10,
            msg="Wrong value for thermal_inertia upper error",
        )

    def test_thermal_inertia_method(self):
        ssocard = rocks.Rock("Steins")
        self.assertIsInstance(
            ssocard.thermal_inertia.method,
            list,
            msg="Wrong class for the thermal_inertia method",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.method[0].doi,
            str,
            msg="Wrong class for the thermal_inertia method - DOI",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.method[0].year,
            int,
            msg="Wrong class for the thermal_inertia method - year",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.method[0].title,
            str,
            msg="Wrong class for the thermal_inertia method - title",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.method[0].bibcode,
            str,
            msg="Wrong class for the thermal_inertia method - bibcode",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.method[0].shortbib,
            str,
            msg="Wrong class for the thermal_inertia method - shortbib",
        )

    def test_thermal_inertia_biblio(self):
        ssocard = rocks.Rock("Steins")
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref,
            list,
            msg="Wrong class for the thermal_inertia bibref",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref[0].doi,
            str,
            msg="Wrong class for the thermal_inertia bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref[0].year,
            int,
            msg="Wrong class for the thermal_inertia bibref - year",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref[0].title,
            str,
            msg="Wrong class for the thermal_inertia bibref - title",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref[0].bibcode,
            str,
            msg="Wrong class for the thermal_inertia bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.thermal_inertia.bibref[0].shortbib,
            str,
            msg="Wrong class for the thermal_inertia bibref - shortbib",
        )


    # --------------------------------------------------------------------------------
    # Test Spin using Psyche
    def test_spin_type(self):
        ssocard = rocks.Rock("Psyche")
        self.assertIsInstance(ssocard.spin, list, msg="Wrong class for the spin")

    def test_spin_period_value(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].period.value,
            4.195948,
            delta=0.00001,
            msg="Wrong value for spin period",
        )

    def test_spin_period_errors(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].period.error.min_,
            -1e-6,
            delta=1e-6,
            msg="Wrong value for spin period lower error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].period.error.max_,
            1e-6,
            delta=1e-6,
            msg="Wrong value for spin period upper error",
        )

    def test_spin_EC_value(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].long_.value,
            35,
            delta=1,
            msg="Wrong value for spin EC longitude",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].lat.value,
            -9,
            delta=1,
            msg="Wrong value for spin EC latitude",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].t0.value, 2451545, delta=1, msg="Wrong value for spin EC t0"
        )

    def test_spin_EQ_value(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].RA0.value,
            34.2,
            delta=1,
            msg="Wrong value for spin EQ right ascencion",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].DEC0.value,
            4.7,
            delta=1,
            msg="Wrong value for spin EQ declination",
        )
        # self.assertAlmostEqual(
        #    ssocard.spin[0].W0.value, 200, delta=5, msg="Wrong value for spin EQ W0"
        # )
        self.assertAlmostEqual(
            ssocard.spin[0].Wp, 2059, delta=1, msg="Wrong value for spin EQ Wp"
        )

    def test_spin_EC_errors(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].long_.error.min_,
            -2,
            delta=1,
            msg="Wrong value for spin EC long lower error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].long_.error.max_,
            2,
            delta=1,
            msg="Wrong value for spin EC long upper error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].lat.error.min_,
            -2,
            delta=1,
            msg="Wrong value for spin EC lat lower error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].lat.error.max_,
            2,
            delta=1,
            msg="Wrong value for spin EC lat upper error",
        )

    def test_spin_EQ_errors(self):
        ssocard = rocks.Rock("Psyche")
        self.assertAlmostEqual(
            ssocard.spin[0].RA0.error.min_,
            -2,
            delta=1,
            msg="Wrong value for spin EC RA0 lower error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].RA0.error.max_,
            2,
            delta=1,
            msg="Wrong value for spin EC RA0 upper error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].DEC0.error.min_,
            -2,
            delta=1,
            msg="Wrong value for spin EC DEC0 lower error",
        )
        self.assertAlmostEqual(
            ssocard.spin[0].DEC0.error.max_,
            2,
            delta=1,
            msg="Wrong value for spin EC DEC0 upper error",
        )

    def test_spin_method(self):
        ssocard = rocks.Rock("Psyche")
        self.assertIsInstance(
            ssocard.spin[0].method,
            list,
            msg="Wrong class for the spin method",
        )
        self.assertIsInstance(
            ssocard.spin[0].method[0].doi,
            str,
            msg="Wrong class for the spin method - DOI",
        )
        self.assertIsInstance(
            ssocard.spin[0].method[0].year,
            int,
            msg="Wrong class for the spin method - year",
        )
        self.assertIsInstance(
            ssocard.spin[0].method[0].title,
            str,
            msg="Wrong class for the spin method - title",
        )
        self.assertIsInstance(
            ssocard.spin[0].method[0].bibcode,
            str,
            msg="Wrong class for the spin method - bibcode",
        )
        self.assertIsInstance(
            ssocard.spin[0].method[0].shortbib,
            str,
            msg="Wrong class for the spin method - shortbib",
        )

    def test_spin_biblio(self):
        ssocard = rocks.Rock("Steins")
        self.assertIsInstance(
            ssocard.spin[0].bibref,
            list,
            msg="Wrong class for the spin bibref",
        )
        self.assertIsInstance(
            ssocard.spin[0].bibref[0].doi,
            str,
            msg="Wrong class for the spin bibref - DOI",
        )
        self.assertIsInstance(
            ssocard.spin[0].bibref[0].year,
            int,
            msg="Wrong class for the spin bibref - year",
        )
        self.assertIsInstance(
            ssocard.spin[0].bibref[0].title,
            str,
            msg="Wrong class for the spin bibref - title",
        )
        self.assertIsInstance(
            ssocard.spin[0].bibref[0].bibcode,
            str,
            msg="Wrong class for the spin bibref - bibcode",
        )
        self.assertIsInstance(
            ssocard.spin[0].bibref[0].shortbib,
            str,
            msg="Wrong class for the spin bibref - shortbib",
        )


    # --------------------------------------------------------------------------------
    # Test colors using Didymos


if __name__ == "__main__":
    unittest.main()
