# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This file contains C++ code needed to export one dimensional static arrays.
"""


namespace = "pyplusplus::convenience"

file_name = "__convenience.pypp.hpp"

code = \
"""// Copyright 2004-2008 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __convenience_pyplusplus_hpp__
#define __convenience_pyplusplus_hpp__

#include "boost/python.hpp"

namespace pyplusplus{ namespace convenience{

//TODO: Replace index_type with Boost.Python defined ssize_t type.
//      This should be done by checking Python and Boost.Python version.
typedef int index_type;

inline void
raise_error( PyObject *exception, const char *message ){
   PyErr_SetString(exception, message);
   boost::python::throw_error_already_set();
}

inline index_type sequence_len(boost::python::object const& obj){
    if( !PySequence_Check( obj.ptr() ) ){
        raise_error( PyExc_TypeError, "Sequence expected" );
    }

    index_type result = PyObject_Length( obj.ptr() );
    if( PyErr_Occurred() ){
        boost::python::throw_error_already_set();
    }
    return result;
}

inline void
ensure_sequence( boost::python::object seq, index_type expected_length=-1 ){
    index_type length = sequence_len( seq );
    if( expected_length != -1 && length != expected_length ){
        std::stringstream err;
        err << "Expected sequence length is " << expected_length << ". "
            << "Actual sequence length is " << length << ".";
        raise_error( PyExc_ValueError, err.str().c_str() );
    }
}

template< class ExpectedType >
void ensure_uniform_sequence( boost::python::object seq, index_type expected_length=-1 ){
    ensure_sequence( seq, expected_length );

    index_type length = sequence_len( seq );
    for( index_type index = 0; index < length; ++index ){
        boost::python::object item = seq[index];

        boost::python::extract<ExpectedType> type_checker( item );
        if( !type_checker.check() ){
            std::string expected_type_name( boost::python::type_id<ExpectedType>().name() );

            std::string item_type_name("different");
            PyObject* item_impl = item.ptr();
            if( item_impl && item_impl->ob_type && item_impl->ob_type->tp_name ){
                item_type_name = std::string( item_impl->ob_type->tp_name );
            }

            std::stringstream err;
            err << "Sequence should contain only items with type \\"" << expected_type_name << "\\". "
                << "Item at position " << index << " has \\"" << item_type_name << "\\" type.";
            raise_error( PyExc_ValueError, err.str().c_str() );
        }
    }
}

template< class Iterator, class Inserter >
void copy_container( Iterator begin, Iterator end, Inserter inserter ){
    for( Iterator index = begin; index != end; ++index )
        inserter( *index );
}

template< class Inserter >
void copy_sequence( boost::python::object const& seq, Inserter inserter ){
    index_type length = sequence_len( seq );
    for( index_type index = 0; index < length; ++index ){
        inserter = seq[index];
    }
}

template< class Inserter, class TItemType >
void copy_sequence( boost::python::object const& seq, Inserter inserter, boost::type< TItemType > ){
    index_type length = sequence_len( seq );
    for( index_type index = 0; index < length; ++index ){
        boost::python::object item = seq[index];
        inserter = boost::python::extract< TItemType >( item );
    }
}

struct list_inserter{
    list_inserter( boost::python::list& py_list )
    : m_py_list( py_list )
    {}
    
    template< class T >
    void operator()( T const & value ){
        m_py_list.append( value );
    }
private:
    boost::python::list& m_py_list;
};

template < class T >
struct array_inserter_t{
    array_inserter_t( T* array, index_type size )
    : m_array( array )
      , m_curr_pos( 0 )
      , m_size( size )
    {}

    void insert( const T& item ){
        if( m_size <= m_curr_pos ){
            std::stringstream err;
            err << "Index out of range. Array size is" << m_size << ", "
                << "current position is" << m_curr_pos << ".";
            raise_error( PyExc_ValueError, err.str().c_str() );
        }
        m_array[ m_curr_pos ] = item;
        m_curr_pos += 1;
    }

    array_inserter_t<T>& 
    operator=( boost::python::object const & item ){
        insert( boost::python::extract< T >( item ) );
        return *this;
    }
    
private:
    T* m_array;
    index_type m_curr_pos;
    const index_type m_size;
};

template< class T>
array_inserter_t<T> array_inserter( T* array, index_type size ){
    return array_inserter_t<T>( array, size );
}

inline boost::python::object 
get_out_argument( boost::python::object result, const char* arg_name ){
    if( !PySequence_Check( result.ptr() ) ){
        return result;
    }    
    boost::python::object cls = boost::python::getattr( result, "__class__" );
    boost::python::object cls_name = boost::python::getattr( cls, "__name__" );
    std::string name = boost::python::extract< std::string >( cls_name );
    if( "named_tuple" == name ){
        return boost::python::getattr( result, arg_name );    
    }
    else{
        return result;
    }
    
}

inline boost::python::object 
get_out_argument( boost::python::object result, index_type index ){
    if( !PySequence_Check( result.ptr() ) ){
        return result;
    }    
    boost::python::object cls = boost::python::getattr( result, "__class__" );
    boost::python::object cls_name = boost::python::getattr( cls, "__name__" );
    std::string name = boost::python::extract< std::string >( cls_name );
    if( "named_tuple" == name ){
        return result[ index ];    
    }
    else{
        return result;
    }
}

} /*pyplusplus*/ } /*convenience*/

namespace pyplus_conv = pyplusplus::convenience;

#endif//__convenience_pyplusplus_hpp__

"""
