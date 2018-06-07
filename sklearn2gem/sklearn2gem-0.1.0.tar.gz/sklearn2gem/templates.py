from mako.template import Template

EXTCONF_RB = Template("""
require 'mkmf'
create_makefile('${gem_name}/${gem_name}')
""")

BINDING_C = Template("""
#include "ruby.h"

void Init_${gem_name}();
VALUE method_predict(VALUE self, VALUE features);

void Init_${gem_name}() {
    VALUE ${class_name} = rb_const_get(rb_cObject, rb_intern("${class_name}"));
	rb_define_method(${class_name}, "predict", method_predict, 1);
}

VALUE method_predict(VALUE self, VALUE features) {
    if(RARRAY_LEN(features) != ${n_features}) {
        rb_raise(rb_eRuntimeError, "Size of array must be ${n_features}");
    }

    double arr[${n_features}];
    for(long i = 0; i < ${n_features}; i++) {
        arr[i] = NUM2DBL(rb_ary_entry(features, i));
    }

    return INT2NUM(predict(arr));
}
""")

GEMSPEC = Template("""
Gem::Specification.new do |s|
  s.name        = '${gem_name}'
  s.version     = '${version}'
  s.summary     = "A ported scikit-learn model"
  s.description = "A ported scikit-learn model"
  s.authors     = ["sklearn2gem"]
  s.files       = [
                    "lib/${gem_name}.rb",
                    "ext/${gem_name}/${gem_name}.c",
                    "ext/${gem_name}/sklearn_model.c"
                  ]
  s.extensions  = ["ext/${gem_name}/extconf.rb"]
end
""")

INIT_RB = Template("""
class ${class_name}
  VERSION = '${version}'
end

require '${gem_name}/${gem_name}'
""")

RAKEFILE = Template("""
require "rake/extensiontask"

Rake::ExtensionTask.new "${gem_name}" do |ext|
  ext.lib_dir = "lib/${gem_name}"
end
""")
