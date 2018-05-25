# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This file contains indexing suite v2 code
"""

file_name = "indexing_suite/multimap.hpp"

code = """// Use, modification and distribution is subject to the Boost Software
// License, Version 1.0. (See accompanying file LICENSE_1_0.txt or copy
// at http://www.boost.org/LICENSE_1_0.txt)
//
// Header file multimap.hpp
//
// Indexing algorithms support for std::multimap instances
//
// History
// =======
// 2006/10/27   Roman     File creation from map.hpp
// 2008/12/08   Roman   Change indexing suite layout
// 2010/04/29   Roman   Adding "__len__" method
//

#ifndef BOOST_PYTHON_INDEXING_MULTIMAP_HPP
#define BOOST_PYTHON_INDEXING_MULTIMAP_HPP

#include <indexing_suite/container_traits.hpp>
#include <indexing_suite/container_suite.hpp>
#include <indexing_suite/algorithms.hpp>
#include <boost/detail/workaround.hpp>
#include <functional>
#include <map>
#include <indexing_suite/pair.hpp>

namespace boost { namespace python { namespace indexing {
  /////////////////////////////////////////////////////////////////////////
  // ContainerTraits implementation for std::map instances
  /////////////////////////////////////////////////////////////////////////

  template<typename Container>
  class multimap_traits : public base_container_traits<Container>
  {
    typedef base_container_traits<Container> base_class;

  public:
# if BOOST_WORKAROUND (BOOST_MSVC, <= 1200)
    // MSVC6 has a nonstandard name for mapped_type in std::multimap
    typedef typename Container::referent_type value_type;
# else
    typedef typename Container::mapped_type value_type;
# endif
    typedef value_type &                    reference;
    typedef typename Container::key_type    index_type; // operator[]
    typedef typename Container::key_type    key_type;   // find, count, ...

    typedef typename BOOST_PYTHON_INDEXING_CALL_TRAITS <value_type>::param_type
      value_param;
    typedef typename BOOST_PYTHON_INDEXING_CALL_TRAITS <key_type>::param_type
      key_param;
    typedef typename BOOST_PYTHON_INDEXING_CALL_TRAITS <index_type>::param_type
      index_param;

    BOOST_STATIC_CONSTANT(
        method_set_type,
        supported_methods = (
              method_iter

            | method_getitem
            | method_contains
            | method_count
            | method_has_key
            | method_len

            | detail::method_set_if<
                  base_class::is_mutable,
                    method_setitem
                  | method_delitem
                  | method_insert
              >::value
        ));
  };

  /////////////////////////////////////////////////////////////////////////
  // Algorithms implementation for std::multimap instances
  /////////////////////////////////////////////////////////////////////////

  template<typename ContainerTraits, typename Ovr = detail::no_override>
  class multimap_algorithms
    : public assoc_algorithms
        <ContainerTraits,
        typename detail::maybe_override
            <multimap_algorithms<ContainerTraits, Ovr>, Ovr>
          ::type>
  {
    typedef multimap_algorithms<ContainerTraits, Ovr> self_type;
    typedef typename detail::maybe_override<self_type, Ovr>::type most_derived;
    typedef assoc_algorithms<ContainerTraits, most_derived> Parent;

  public:
    typedef typename Parent::container container;
    typedef typename Parent::reference reference;
    typedef typename Parent::index_param index_param;
    typedef typename Parent::value_param value_param;

    static boost::python::list get (container &, index_param);
    // Version to return only the mapped type

    static boost::python::list keys( container & );

    static void      assign     (container &, index_param, value_param);
    static void      insert     (container &, index_param, value_param);

    template<typename PythonClass, typename Policy>
    static void visit_container_class( PythonClass &pyClass, Policy const &policy)
    {
      ContainerTraits::visit_container_class (pyClass, policy);
      pyClass.def( "keys", &self_type::keys );

      typedef BOOST_DEDUCED_TYPENAME most_derived::container::value_type value_type;
      mapping::register_value_type< PythonClass, value_type, Policy >( pyClass );
      //now we can expose iterators functionality
      pyClass.def( "__iter__", python::iterator< BOOST_DEDUCED_TYPENAME most_derived::container >() );

    }

  };

  template<
    class Container,
    method_set_type MethodMask = all_methods,
    class Traits = multimap_traits<Container>
  >
  struct multimap_suite
    : container_suite<Container, MethodMask, multimap_algorithms<Traits> >
  {
  };

  /////////////////////////////////////////////////////////////////////////
  // Index into a container (multimap version)
  /////////////////////////////////////////////////////////////////////////

  template<typename ContainerTraits, typename Ovr>
  boost::python::list
  multimap_algorithms<ContainerTraits, Ovr>::get (container &c, index_param ix)
  {
    boost::python::list l;
    typedef BOOST_DEDUCED_TYPENAME container::iterator iter_type;
    for( iter_type index = c.lower_bound( ix ); index != c.upper_bound( ix ); ++index ){
        boost::python::object v( index->second );
        l.append( v );
    }
    return l;
  }

  template<typename ContainerTraits, typename Ovr>
  boost::python::list
  multimap_algorithms<ContainerTraits, Ovr>::keys( container &c )
  {
    boost::python::list _keys;
    //For some reason code with set could not be compiled
    //std::set< key_param > unique_keys;
    typedef BOOST_DEDUCED_TYPENAME container::iterator iter_type;
    for( iter_type index = most_derived::begin(c); index != most_derived::end(c); ++index ){
        //if( unique_keys.end() == unique_keys.find( index->first ) ){
        //    unique_keys.insert( index->first );
        if( !_keys.count( index->first ) ){
            _keys.append( index->first );
        }
        //}
    }

    return _keys;
  }


  /////////////////////////////////////////////////////////////////////////
  // Assign a value at a particular index (map version)
  /////////////////////////////////////////////////////////////////////////

  template<typename ContainerTraits, typename Ovr>
  void
  multimap_algorithms<ContainerTraits, Ovr>::assign(
      container &c, index_param ix, value_param val)
  {
    typedef std::pair<
        BOOST_DEDUCED_TYPENAME self_type::container_traits::index_type
        , BOOST_DEDUCED_TYPENAME self_type::container_traits::value_type>
    pair_type;

    // Can't use std::make_pair, because param types may be references
    c.insert (pair_type (ix, val));
  }


  /////////////////////////////////////////////////////////////////////////
  // Insert a new key, value pair into a map
  /////////////////////////////////////////////////////////////////////////

  template<typename ContainerTraits, typename Ovr>
  void
  multimap_algorithms<ContainerTraits, Ovr>::insert(
      container &c, index_param ix, value_param val)
  {
    typedef std::pair
      <BOOST_DEDUCED_TYPENAME self_type::container_traits::index_type,
      BOOST_DEDUCED_TYPENAME self_type::container_traits::value_type>
      pair_type;

    // Can't use std::make_pair, because param types may be references
    c.insert (pair_type (ix, val) );
  }
} } }

#endif // BOOST_PYTHON_INDEXING_MULTIMAP_HPP


"""
